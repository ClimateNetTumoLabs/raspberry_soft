#!/bin/bash
#
# Stop at the first failure. Without this every command here was advisory: a
# station came up with an empty virtualenv, this script printed "Installation
# completed successfully", and ProgramAutoRun crash-looped on
# `ModuleNotFoundError: No module named 'dotenv'` - see the venv section below
# for the chain. It is usually run unattended, by something that installs a
# station rather than by someone watching it, so an exit code is the only way
# it can report anything at all.
set -e

# Where this checkout actually lives, and who owns it.
#
# The unit files ship with /home/raspberry paths and User=raspberry as their
# defaults, but nothing requires that name: the Imager dialog creates whatever
# account it was told to, and a station set up under any other one got units
# pointing at a directory that does not exist and a user that does not either -
# so ProgramAutoRun failed to start and nothing said why. They are rewritten
# with these two values as they are copied into /etc/systemd/system, which git
# does not track, so ServiceFiles/ stays clean and `git pull` never conflicts.
#
# STATION_USER can be passed in, for a caller that already knows the account
# and should not have it guessed at a second time.
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
STATION_USER="${STATION_USER:-$(stat -c '%U' "$REPO_DIR")}"
echo "Installing for user '${STATION_USER}' from ${REPO_DIR}"

# None of these ship with Raspberry Pi OS Lite, and all are no-ops on a station
# that already has them:
#   python3-venv       - ensurepip, without which `python3 -m venv` leaves a
#                        directory with a python in it and no pip. That is the
#                        whole of the bug above: the venv looked created, the
#                        install carried on, and the requirements went to the
#                        system python instead.
#   swig, liblgpio-dev - build lgpio, which has no prebuilt wheel for 64-bit
#   python3-dev        - Python.h, needed by lgpio, rpi-ws281x, RPi.GPIO, sysv-ipc
#   vim                - set as git's core.editor a few lines down
sudo apt install -y swig liblgpio-dev python3-dev python3-venv vim

# Enable interfaces
sudo raspi-config nonint do_ssh 0
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial_cons 1
sudo raspi-config nonint do_serial_hw 0

# Configure git editor
git config --global core.editor "vim"

echo "dtoverlay=pi3-miniuart-bt" | sudo tee -a /boot/firmware/config.txt
echo "dtoverlay=pi3-miniuart-bt" | sudo tee -a /boot/config.txt

# Copy the units, substituting this station's user and checkout path. The two
# expressions are deliberately narrow: a blanket s/raspberry/$STATION_USER/
# would also rewrite "raspberry_soft" in every path it appears in, and the
# anchors on User=/Group= keep it to the two lines that name an account.
#
# Through sudo and by absolute path, like everything else here: with `set -e` a
# failure writing into /etc is now fatal rather than a warning nobody reads,
# and it should fail on not being root rather than on the current directory
# happening to be somewhere else.
for unit in WifiMonitor.service ProgramAutoRun.service; do
    sed -e "s|/home/raspberry/workspace/raspberry_soft|${REPO_DIR}|g" \
        -e "s|^User=raspberry$|User=${STATION_USER}|" \
        -e "s|^Group=raspberry$|Group=${STATION_USER}|" \
        "$REPO_DIR/ServiceFiles/$unit" | sudo tee "/etc/systemd/system/$unit" >/dev/null
done

sudo chmod +x "$REPO_DIR/ServiceFiles/wifi_monitor.sh"

# The virtualenv, addressed through its own interpreter rather than through
# `source activate` and a bare `pip`.
#
# Activating only prepends a directory to PATH, and `pip` is then whatever that
# finds. A venv with no pip of its own - the one `python3 -m venv` leaves
# behind when ensurepip is missing, and the one carried over from an image
# whose python has since moved a minor version - lets `pip` fall through to
# /usr/bin/pip, which installs into the system python and, on Raspberry Pi OS
# before PEP 668 was enforced, exits 0 while doing it. The requirements land
# somewhere nothing reads and ProgramAutoRun dies on `import dotenv`, which is
# main.py's first third-party import by way of config.py.
#
# `venv/bin/python3 -m pip` cannot install anywhere but the venv. ensurepip
# repairs a venv that has lost its own pip; it is a no-op on a healthy one.
# Deliberately not `--clear`: prepare_image.sh keeps the built venv in the
# golden image precisely because lgpio costs about half an hour to compile.
VENV="${REPO_DIR}/app/venv"
python3 -m venv "$VENV"
"$VENV/bin/python3" -m ensurepip --upgrade >/dev/null 2>&1 || true
"$VENV/bin/python3" -m pip install --upgrade pip
"$VENV/bin/python3" -m pip install -r "${REPO_DIR}/app/requirements.txt"

# The one thing that has to be true when the step above returns, checked rather
# than assumed. Nothing after this line would notice: `systemctl start` on a
# Type=simple unit returns as soon as the process is forked, so a station whose
# program dies on its first import still reaches the success message below.
if ! "$VENV/bin/python3" -c 'import dotenv, paho.mqtt.client, requests'; then
    echo "ERROR: ${VENV} cannot import what main.py needs - see above" >&2
    exit 1
fi

# Reload systemd to recognize new service files
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager

sudo systemctl enable WifiMonitor.service
sudo systemctl start WifiMonitor.service

sudo systemctl enable ProgramAutoRun.service
sudo systemctl start ProgramAutoRun.service

echo "Installation completed successfully."
