#!/bin/bash
#
# Generate the Raspberry Pi Imager repository metadata for the station base image.
#
#   ./make_os_list.sh                                  # local test, file:// URL
#   URL=https://github.com/.../base.img.gz ./make_os_list.sh    # for publishing
#
# Imager only offers the OS customisation dialog (hostname, user, Wi-Fi, SSH,
# locale) for images it knows how to configure. Selecting a file through
# "Use custom" tells it nothing, so the dialog is suppressed. Declaring the image
# in a repository with init_format is what enables it.
#
# init_format is cloudinit-rpi because the base is official Raspberry Pi OS Lite,
# which declares exactly that in downloads.raspberrypi.org/os_list_imagingutility_v4.json.
# Plain "cloudinit" is a different, non-Raspberry-Pi flavour - it will not apply
# the Pi-specific settings.
#
# Runs on macOS and Linux. The two tools that differ between them are resolved below.
# On Windows use WSL or Git Bash - building an SD image needs a POSIX shell either way.

set -eu

# GNU coreutils on Linux, BSD equivalents on macOS.
if command -v sha256sum >/dev/null 2>&1; then
    sha256_of() { sha256sum | awk '{print $1}'; }
else
    sha256_of() { shasum -a 256 | awk '{print $1}'; }
fi
file_size() { stat -c%s "$1" 2>/dev/null || stat -f%z "$1"; }

IMG="${1:-$HOME/climatenet-base.img.gz}"
[ -f "$IMG" ] || { echo "no image at $IMG" >&2; exit 1; }

IMG_DIR="$(cd "$(dirname "$IMG")" && pwd)"
IMG_NAME="$(basename "$IMG")"

# The metadata is written beside the image, so the two stay together as a pair.
OUT="${2:-${IMG_DIR}/os_list.json}"

# Imager passes this straight to libcurl, which needs a real scheme: a bare filename
# is parsed as a hostname ("Could not resolve host: climatenet-base.img.gz") and ~ or
# $VARS are never expanded. So a local URL has to be an absolute file:// path, and
# that path ends up in the file.
#
# To keep a username out of it, build in a neutral directory - /Users/Shared/... on
# macOS - or publish and pass the real URL:
#     URL=https://github.com/.../climatenet-base.img.gz ./make_os_list.sh
URL="${URL:-file://${IMG_DIR}/${IMG_NAME}}"
# pi3-64bit is the Imager tag for Raspberry Pi 3. Add pi4-64bit / pi5-64bit only if
# stations actually run on those - the dtoverlay install.sh writes is Pi 3 specific.
DEVICES="${DEVICES:-\"pi3-64bit\"}"

# extract_size and extract_sha256 describe the UNCOMPRESSED image, so both come from
# decompressing. Done in one pass because the image is ~16 GB. gzip -l is not usable
# here: it reports size modulo 4 GB and would silently be wrong.
echo "hashing and measuring the uncompressed image, this takes a few minutes..." >&2
SZFILE="$(mktemp)"
SHA="$(gunzip -c "$IMG" | tee >(wc -c | tr -d ' ' > "$SZFILE") | sha256_of)"
EXTRACT="$(cat "$SZFILE")"
rm -f "$SZFILE"

DOWNLOAD="$(file_size "$IMG")"

# The "imager" block is what populates Imager's device chooser. Without it the
# wizard shows "No device selected" and the OS entry is filtered out by its own
# devices tag. Entries copied verbatim from Raspberry Pi's official
# os_list_imagingutility_v4.json so the chooser looks and behaves as users expect.
# Only Pi 3 is offered because install.sh writes a Pi 3 specific dtoverlay.
cat > "$OUT" <<JSON
{
  "imager": {
    "latest_version": "2.0.10",
    "url": "https://www.raspberrypi.com/software/",
    "devices": [
      {
        "name": "Raspberry Pi 3",
        "tags": ["pi3-64bit", "pi3-32bit"],
        "default": true,
        "icon": "https://downloads.raspberrypi.com/imager/icons/RPi_3.png",
        "description": "Raspberry Pi 3 Model A+ / B / B+ and Compute Module 3 / 3+",
        "matching_type": "inclusive",
        "capabilities": []
      },
      {
        "name": "No filtering",
        "tags": [],
        "default": false,
        "description": "Show every possible image",
        "matching_type": "inclusive",
        "capabilities": []
      }
    ]
  },
  "os_list": [
    {
      "name": "ClimateNet Station Base",
      "description": "Raspberry Pi OS Lite 64-bit with ClimateNet first-boot setup",
      "url": "${URL}",
      "release_date": "$(date +%F)",
      "image_download_size": ${DOWNLOAD},
      "extract_size": ${EXTRACT},
      "extract_sha256": "${SHA}",
      "init_format": "cloudinit-rpi",
      "devices": [${DEVICES}]
    }
  ]
}
JSON

echo "wrote $OUT" >&2
echo "  download   ${DOWNLOAD} bytes" >&2
echo "  extract    ${EXTRACT} bytes" >&2
echo "  sha256     ${SHA}" >&2
