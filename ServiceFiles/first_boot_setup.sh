#!/bin/bash
#
# First-boot setup for a station flashed from the ClimateNet base image.
#
# Not run by install.sh and not installed by it. This lives at
# /usr/local/sbin/first_boot_setup.sh in the image, driven by FirstBootSetup.service,
# and runs exactly once - after Imager's custom.toml has applied the hostname, user
# password, locale, ssh and Wi-Fi settings, and after the network is up.
#
# It clones the repo and runs install.sh, so the image itself carries neither the
# checkout nor the venv. That keeps the image small and keeps stations from being
# born on stale code.
#
# It deliberately stops short of a working station: .env, the AWS IoT certificates
# and this unit's calibration cannot be baked into a shared image, so it leaves
# ProgramAutoRun disabled and a checklist in the user's home directory.

set -eu

REPO_URL="${REPO_URL:-https://github.com/ClimateNetTumoLabs/raspberry_soft.git}"
BRANCH="${BRANCH:-main}"
# Hardcoded rather than detected: the service units, wifi_monitor.sh and install.sh
# all hardcode this user, so a station under any other name would install and then
# quietly do nothing.
STATION_USER="${STATION_USER:-raspberry}"
TARGET="/home/${STATION_USER}/workspace/raspberry_soft"
STAMP=/var/lib/climatenet/setup-done

die() { echo "FAIL: $*" >&2; exit 1; }

id "$STATION_USER" >/dev/null 2>&1 \
    || die "no user '$STATION_USER' - the image requires this username, set it in Raspberry Pi Imager"

# Package lists are empty on a fresh image, so install.sh's apt install would fail
# to find swig and liblgpio-dev. Done here rather than in install.sh, which runs on
# already-provisioned stations where this is just a slow no-op.
#
# Retried once because the first attempt runs seconds after boot, before NTP has
# corrected the clock: apt then fetches indexes against a wrong date and reports
# "Some index files failed to download" as a warning, exiting 0 with a half-built
# index that makes the install below fail for no visible reason.
apt-get update || apt-get update

# Raspberry Pi OS Lite ships no git, and cloning is this script's entire purpose.
apt-get install -y git

# Clone as the station user. A root-owned checkout makes every later git command run
# as raspberry fail with git's dubious-ownership check.
if [ ! -d "$TARGET/.git" ]; then
    # An aborted earlier attempt can leave a directory with no .git in it.
    rm -rf "$TARGET"
    runuser -u "$STATION_USER" -- mkdir -p "$(dirname "$TARGET")"
    runuser -u "$STATION_USER" -- git clone --branch "$BRANCH" "$REPO_URL" "$TARGET"
fi

# install.sh expects to run from the repo root, as root, exactly as it is run by hand.
cd "$TARGET"
chmod +x install.sh
./install.sh

# install.sh enables and starts ProgramAutoRun. There is no .env yet, so leaving it
# running means a crash loop writing to the SD card until somebody provisions it.
systemctl disable --now ProgramAutoRun.service >/dev/null 2>&1 || true

cat > "/home/${STATION_USER}/PROVISION_ME.txt" <<'EOF'
This station was flashed from the ClimateNet base image. The code and virtualenv
are installed; the station-specific parts are not. ProgramAutoRun stays disabled
until you finish these steps.

  1. cp app/env_template app/.env   and fill in DEVICE_ID, MQTT_TOPIC,
     MQTT_BROKER_ENDPOINT, MQTT_ACK_TOPIC, LATITUDE, LONGITUDE
  2. copy this device's certificates into app/utils/certificates/
     (rootCA.pem, certificate.pem.crt, private.pem.key)
  3. edit app/config.py: SSID and PASSWORD, the SENSORS working flags for this
     hardware build, and this unit's calibration (adc_vref, speed_coefficient,
     bucket_size, and the 16 wind-vane volts)
  4. sudo reboot        # install.sh added dtoverlay=pi3-miniuart-bt; the UART
                        # sensors do not work until this has been applied
  5. cd app && venv/bin/python testing.py     # every sensor should report
  6. sudo systemctl enable --now ProgramAutoRun
  7. rm ~/PROVISION_ME.txt

Setup log:  journalctl -u FirstBootSetup
EOF
chown "$STATION_USER":"$STATION_USER" "/home/${STATION_USER}/PROVISION_ME.txt"

mkdir -p "$(dirname "$STAMP")"
touch "$STAMP"
echo "first boot setup complete - see /home/${STATION_USER}/PROVISION_ME.txt"
