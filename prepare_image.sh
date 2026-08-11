#!/bin/bash
#
# Strip per-station identity from a working station so its SD card can be cloned
# into a golden image.
#
# Run this ON the station, as the last thing before shutting down:
#     sudo ./prepare_image.sh && sudo shutdown -h now
# then pull the card and image it from another machine (never dd a mounted rootfs).
#
# What survives: the OS, apt packages, the built venv (including the lgpio
# extension that costs ~30 min to compile on a Pi 3), and the git checkout.
# What does not: anything that names or tunes THIS station.
#
# This is destructive and one-way. The station it runs on stops being a working
# station until it is provisioned again - that is the point.

set -eu

STATION_USER="${STATION_USER:-raspberry}"
REPO="${REPO:-/home/${STATION_USER}/workspace/raspberry_soft}"
APP="${REPO}/app"
BOOTCFG="${BOOTCFG:-/boot/firmware/config.txt}"

die() { echo "FAIL: $*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run with sudo"

echo "This strips host identity, logs and caches from this card, and any"
echo "station data on it (.env, certificates, calibration). One way."
printf "Type 'strip' to continue: "
read -r reply
[ "$reply" = "strip" ] || die "aborted"

# ---------------------------------------------------------------- app state
# Absent when building the base image from a stock Lite install, where the checkout
# arrives at first boot instead. Present when cloning a working station.
if [ -d "$REPO/.git" ]; then
    # .env is gitignored and per-station; env_template is the checklist for refilling it.
    rm -f "$APP/.env"

    # Per-device AWS IoT credential. Delete even if your fleet shares one cert: an
    # image file is copied and passed around far more casually than a station is.
    rm -f "$APP"/utils/certificates/*.pem "$APP"/utils/certificates/*.crt \
          "$APP"/utils/certificates/*.key

    # Unsent records. Left in place, every station flashed from this image republishes
    # the golden station's measurements under its own DEVICE_ID.
    rm -f "$APP"/local_data.json "$APP"/local_data.json.tmp "$APP"/local_data.json.corrupt.*
    rm -f "$APP/parsing.log"

    # config.py is tracked but edited in place on every station (Wi-Fi credentials,
    # working flags, calibration). Resetting to the committed version clears this
    # station's values AND leaves a clean tree, so the first git pull on a new station
    # cannot conflict. Tuned numbers are per-unit anyway - a cloned vane calibration is
    # worse than no calibration, because it looks plausible.
    runuser -u "$STATION_USER" -- git -C "$REPO" checkout -- app/config.py

    find "$REPO" -name __pycache__ -type d -prune -exec rm -rf {} +
    echo "stripped station data from $REPO"
else
    echo "no checkout at $REPO - base image build, nothing station-specific to strip"
fi

# The service must not crash-loop on an unprovisioned station; provisioning re-enables it.
systemctl disable ProgramAutoRun.service >/dev/null 2>&1 || true

# ---------------------------------------------------------------- host identity
# Empty, NOT deleted: systemd regenerates an empty machine-id on boot but treats a
# missing one as a fatal error.
: > /etc/machine-id
[ -L /var/lib/dbus/machine-id ] || rm -f /var/lib/dbus/machine-id

rm -f /etc/ssh/ssh_host_*
if systemctl list-unit-files | grep -q '^regenerate_ssh_host_keys'; then
    systemctl enable regenerate_ssh_host_keys.service >/dev/null 2>&1
else
    echo "WARN: no regenerate_ssh_host_keys.service - run" >&2
    echo "      'sudo dpkg-reconfigure openssh-server' on each new station" >&2
fi

# Saved Wi-Fi profiles hold the PSK in cleartext, separately from config.py.
rm -f /etc/NetworkManager/system-connections/*

# ------------------------------------------------- re-arm first-boot customisation
# Raspberry Pi OS applies /boot/firmware/custom.toml (hostname, ssh, wlan) on first
# boot via raspberrypi-sys-mods, then removes its own init= from cmdline.txt. This
# station already consumed it; putting it back re-arms every card flashed from the
# resulting image. Verified here rather than assumed - if the paths differ on your
# OS release, this warns instead of silently producing an image that ignores the file.
# Newer Raspberry Pi OS takes Imager's settings through cloud-init (NoCloud seed on
# the boot partition) rather than custom.toml. cloud-init records that it already ran
# and will not re-read the seed until that state is cleared, so a card flashed from
# this image would ignore everything typed into the Imager dialog.
CLOUD_INIT=0
if command -v cloud-init >/dev/null 2>&1; then
    if cloud-init clean --logs --seed >/dev/null 2>&1; then
        CLOUD_INIT=1
        echo "cloud-init state cleared - seed will be re-read on first boot"
    else
        echo "WARN: cloud-init clean failed" >&2
    fi
fi

# The older, pre-cloud-init mechanism. An image has one or the other, not both, so a
# missing firstboot is only a problem when cloud-init is absent too.
FIRSTBOOT=/usr/lib/raspberrypi-sys-mods/firstboot
CMDLINE="${CMDLINE:-/boot/firmware/cmdline.txt}"
if [ -x "$FIRSTBOOT" ] && [ -f "$CMDLINE" ]; then
    if grep -q "init=${FIRSTBOOT}" "$CMDLINE"; then
        echo "first-boot customisation already armed"
    else
        # cmdline.txt must remain exactly one line - append, never add a newline.
        sed -i "1s|\$| init=${FIRSTBOOT}|" "$CMDLINE"
        echo "re-armed first-boot customisation in $CMDLINE"
    fi
elif [ "$CLOUD_INIT" -eq 1 ]; then
    echo "no raspberrypi-sys-mods firstboot - this image customises via cloud-init"
else
    echo "WARN: neither cloud-init nor $FIRSTBOOT present - flashed cards will ignore" >&2
    echo "      Imager's settings; set hostname and Wi-Fi by hand during provisioning" >&2
fi

# ---------------------------------------------------------------- shrink the image
# install.sh appends its dtoverlay unconditionally, so a station installed more than
# once accumulates duplicates. Harmless at boot, but they compound on every reimage.
if [ -f "$BOOTCFG" ]; then
    awk '!(/^dtoverlay=pi3-miniuart-bt$/ && seen++)' "$BOOTCFG" > "${BOOTCFG}.new" \
        && mv "${BOOTCFG}.new" "$BOOTCFG"
fi

apt-get clean
rm -rf /root/.cache/pip "/home/${STATION_USER}/.cache/pip"
rm -f /root/.bash_history "/home/${STATION_USER}/.bash_history"
journalctl --rotate >/dev/null 2>&1 || true
journalctl --vacuum-time=1s >/dev/null 2>&1 || true
find /var/log -type f \( -name '*.gz' -o -name '*.[0-9]' \) -delete

# Zero free space so the image compresses. Costs a few minutes and a lot of writes;
# skip with ZEROFILL=0 if you are going to shrink the image with pishrink anyway.
if [ "${ZEROFILL:-1}" = "1" ]; then
    echo "zeroing free space - this fills the disk on purpose, so the"
    echo "'No space left on device' below is how it is meant to end"
    dd if=/dev/zero of=/zero.fill bs=4M status=none || true
    rm -f /zero.fill
    sync
    echo "free space zeroed, $(df -h / | awk 'NR==2{print $4}') available again"
fi

cat > "/home/${STATION_USER}/PROVISION_ME.txt" <<'EOF'
This station was flashed from a golden image and is NOT yet provisioned.
ProgramAutoRun is disabled until you finish these steps.

  1. cp app/env_template app/.env   and fill in DEVICE_ID, MQTT_TOPIC,
     MQTT_BROKER_ENDPOINT, MQTT_ACK_TOPIC, LATITUDE, LONGITUDE
  2. copy this device's certs into app/utils/certificates/
     (rootCA.pem, certificate.pem.crt, private.pem.key)
  3. edit app/config.py: SSID, PASSWORD, the SENSORS working flags for this
     build, and this unit's calibration (adc_vref, speed_coefficient,
     bucket_size, and the 16 wind-vane volts)
  4. cd app && venv/bin/python testing.py     # every sensor should report
  5. sudo systemctl enable --now ProgramAutoRun
  6. rm ~/PROVISION_ME.txt
EOF
chown "$STATION_USER":"$STATION_USER" "/home/${STATION_USER}/PROVISION_ME.txt"

echo
echo "Stripped. Now: sudo shutdown -h now, then image the card from another machine."
