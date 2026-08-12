# ClimateNet station base image

Building a custom Raspberry Pi OS image so a new weather station can be flashed,
configured through the Raspberry Pi Imager dialog, and set itself up on first boot.

**Status: paused 2026-08-12.** Work lives on branch `custom-rpi-image`, unmerged.
Nothing is published. See [Where this was left](#where-this-was-left) before resuming.

---

## Why this exists

Setting up a station by hand means flashing stock Raspberry Pi OS, cloning the repo
and running `install.sh` on every unit. On 64-bit that install is slow: `lgpio` has no
prebuilt wheel for Python 3.13/aarch64, so it compiles from source on a Pi 3.

### The design decision

The obvious approach - set up one station perfectly, clone its SD card - was rejected.
A card holds too much that is unique to one unit: `.env`, AWS IoT certificates, Wi-Fi
credentials, wind-vane calibration, unsent measurements, SSH host keys, machine-id.
Cloning those means every station reports as `device54` and shares one identity.

Instead the image is **deliberately thin**:

| In the image                                 | Not in the image                          |
| -------------------------------------------- | ----------------------------------------- |
| Raspberry Pi OS Lite 64-bit                  | The repo checkout                         |
| `/usr/local/sbin/first_boot_setup.sh`        | The virtualenv                            |
| `/etc/systemd/system/FirstBootSetup.service` | `.env`, certificates, calibration         |
| SSH host key regeneration unit               | SSH host keys, machine-id, Wi-Fi profiles |

Everything else arrives at first boot by cloning the repo and running `install.sh`.

Two consequences worth knowing:

- **Most fixes need no image rebuild.** Anything in `install.sh` or the app arrives
  through the clone. Only changes to `FirstBootSetup.service` or
  `first_boot_setup.sh` require rebuilding.
- **Stations are never born on stale code**, because they clone at first boot.

### Boot sequence

```
Imager writes cloud-init seed → boot partition
        ↓
cloud-init applies hostname / user / password / Wi-Fi / SSH / locale
        ↓
network-online.target
        ↓
FirstBootSetup: apt-get update → install git → clone repo → install.sh
        ↓
disables ProgramAutoRun, writes ~/PROVISION_ME.txt, touches the done-stamp
        ↓
[manual] .env + certificates + calibration → enable ProgramAutoRun
```

---

## Files

| File                                  | Runs on             | Purpose                                                                                                              |
| ------------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `ServiceFiles/first_boot_setup.sh`    | station, first boot | Clones the repo and runs `install.sh`. Baked into the image at `/usr/local/sbin/`, **not** installed by `install.sh` |
| `ServiceFiles/FirstBootSetup.service` | station, first boot | Drives the above. Carries `BRANCH` and `HOME`                                                                        |
| `prepare_image.sh`                    | build card, once    | Strips host identity and station data, arms SSH key regeneration, resets cloud-init, zero-fills free space           |
| `make_os_list.sh`                     | macOS               | Generates `os_list.json`, the Imager repository metadata                                                             |
| `install.sh`                          | station             | Unchanged role, but now derives user/path and installs the Lite-missing packages                                     |

---

## Two things that were not obvious

### 1. The Imager customisation dialog requires repository metadata

Selecting a file through **"Use custom"** never shows the hostname/user/Wi-Fi dialog.
Imager gates it on an `init_format` field, and a hand-picked file carries no metadata
to declare one. This is by design and cannot be worked around from inside the image.

The fix is to serve the image through a repository JSON. Then it appears as a normal
entry in the OS list - better than "Use custom" anyway, since nobody has to browse for
a file.

`init_format` must be **`cloudinit-rpi`**, not `cloudinit`. Verified against Raspberry
Pi's own list, where Raspberry Pi OS Lite 64-bit declares exactly that:

```bash
curl -s https://downloads.raspberrypi.org/os_list_imagingutility_v4.json | python3 -m json.tool | grep -A2 init_format | head
```

The `imager.devices` block is separately required - without it the wizard shows
"No device selected" and filters out the OS entry.

### 2. The `url` field is a URL, not a path

Imager hands it to libcurl. A bare filename is parsed as a hostname
(`Could not resolve host: climatenet-base.img.gz`), and `~` and `$VARS` are never
expanded. A local image needs an absolute `file://` URL.

To keep a username out of the committed metadata, the image lives in
`/Users/Shared/climatenet-image/`. Once published, pass the real URL and no local path
is recorded at all.

---

## Where this was left

### Works, verified

- The full first-boot chain, on a station patched by hand: clone → `apt` → venv →
  compile `lgpio` → units installed → `PROVISION_ME.txt` written. Finished clean.
- `install.sh` runs unattended under `set -e`.
- Username is no longer hardcoded: units are rewritten with the real user and path as
  they are copied into `/etc/systemd/system/`, so `ServiceFiles/` stays clean and
  `git pull` never conflicts.
- Imager shows the customisation dialog and generates correct cloud-init YAML.

### Not verified

- **A clean unattended boot from the rebuilt image.** This is the one test that
  matters and it has never been completed. The current image was captured after all
  fixes were pushed, so it _should_ be correct, but nothing has proved it.
- Whether Imager accepts the `file://` URL after the fix. The last known run failed on
  the relative path; the URL was corrected afterwards but not retested.
- Whether Imager's APP OPTIONS repository setting persists across restarts. If it
  does, no launcher script is needed for production.

### Stale / incomplete

- **`make_os_list.sh` has an uncommitted fix.** Commit `7095570` contains the broken
  relative-path version. Commit the working tree before doing anything else.
- Nothing is published. No GitHub release, no hosted `os_list.json`.
- `ServiceFiles/FirstBootSetup.service` still carries `Environment=BRANCH=custom-rpi-image`.
  **Remove that line when merging to `main`**, or every station will keep tracking the
  branch forever.

---

## Rebuilding the image

### 1. On your Mac (GUI) - flash stock Lite to the build card

Raspberry Pi Imager → **Raspberry Pi OS Lite (64-bit)**, under "Raspberry Pi OS (other)".
Customisation: username `raspberry`, your Wi-Fi, SSH enabled. Write, then boot the Pi.

Use the smallest card you have - `dd` captures the whole card, and `extract_size`
determines how long every future flash takes.

### 2. On your Mac - copy the three files

```bash
cd /Users/davit/workspace/raspberry_soft && scp ServiceFiles/first_boot_setup.sh ServiceFiles/FirstBootSetup.service prepare_image.sh raspberry@raspberrypi.local:~
```

### 3. On the build Pi - install the bootstrap

Not enabled yet: an armed unit plus one reboot would build an entire station into the
image you are trying to keep thin.

```bash
sudo install -m 755 ~/first_boot_setup.sh /usr/local/sbin/ && sudo install -m 644 ~/FirstBootSetup.service /etc/systemd/system/ && rm ~/first_boot_setup.sh ~/FirstBootSetup.service
```

### 4. On the build Pi - verify before committing to a build

```bash
grep Environment /etc/systemd/system/FirstBootSetup.service
```

Must show **both** `BRANCH=custom-rpi-image` and `HOME=/root`. Without `HOME`,
`install.sh` dies at `git config --global` with `fatal: $HOME not set`.

### 5. On the build Pi - arm and strip

```bash
sudo systemctl enable FirstBootSetup.service && sudo ~/prepare_image.sh
```

Type `strip`. Expected output:

- `no checkout at ... - base image build` - correct, the repo is not in the image
- `ssh host keys removed, regeneration armed for first boot`
- `cloud-init state cleared`
- `no raspberrypi-sys-mods firstboot - this image customises via cloud-init`
- `No space left on device` during the zero-fill - **this is the success condition**,
  the disk is filled with zeros on purpose so the image compresses

### 6. On the build Pi - shut down

```bash
rm -f ~/prepare_image.sh && sudo shutdown -h now
```

Wait for the green LED to go dark before pulling the card. Never image a mounted
filesystem.

### 7. On your Mac - capture

```bash
diskutil list
```

Identify the card by size and by its `bootfs` + `Linux` partitions. Then, substituting
the real identifier:

```bash
diskutil unmountDisk /dev/disk5 && mkdir -p /Users/Shared/climatenet-image && sudo dd if=/dev/rdisk5 bs=4m | gzip > /Users/Shared/climatenet-image/climatenet-base.img.gz
```

`rdisk` is the raw device and is far faster. BSD `dd` prints no progress - press
**Ctrl-T** for a status line.

### 8. On your Mac - generate the metadata

Required after every rebuild: the SHA changes and Imager verifies against it.

```bash
cd /Users/davit/workspace/raspberry_soft && ./make_os_list.sh /Users/Shared/climatenet-image/climatenet-base.img.gz && cat /Users/Shared/climatenet-image/os_list.json
```

Streams the whole uncompressed image through `gunzip` to hash it - a few minutes.

### 9. On your Mac - test

```bash
"/Applications/Raspberry Pi Imager.app/Contents/MacOS/rpi-imager" --repo "/Users/Shared/climatenet-image/os_list.json"
```

"ClimateNet Station Base" should appear as a listed OS with Raspberry Pi 3
preselected, and selecting it should offer the customisation dialog.

---

## Flashing and provisioning a station

1. Flash from the list entry. Fill in hostname, locale, Wi-Fi, SSH.
   **Username must be `raspberry`** unless you rebuild - see below.
2. Boot and wait. The clone plus `install.sh` takes 20-40 minutes on a Pi 3, mostly
   compiling `lgpio`.

```bash
ssh raspberry@<hostname>.local 'journalctl -u FirstBootSetup -f'
```

3. Success looks like `setting up for user 'raspberry' in ...` at the start and
   `first boot setup complete` at the end.

```bash
ls -l /var/lib/climatenet/setup-done ~/PROVISION_ME.txt && systemctl is-enabled ProgramAutoRun WifiMonitor
```

Expect both files present, `ProgramAutoRun` **disabled**, `WifiMonitor` **enabled**.

4. Then the per-station work listed in `~/PROVISION_ME.txt`: `.env`, the AWS IoT
   certificates, `config.py` (Wi-Fi credentials, `SENSORS` working flags, and this
   unit's calibration), reboot for the UART overlay, verify with `testing.py`, then
   `sudo systemctl enable --now ProgramAutoRun`.

### About the username

`install.sh` derives the user from the checkout's owner and rewrites the units as it
copies them, so **any username works**. `first_boot_setup.sh` finds the account at uid
1000, whichever name cloud-init gave it.

`raspberry` is still the safe choice because the existing fleet uses it and
`upgrade_station.sh` defaults to it.

---

## Bug history

Every one of these was a package or environment assumption that held on the existing
32-bit station and did not on a bare Lite image. Useful if new failures appear.

| Symptom                                          | Cause                                                                                                                                        | Fix                                                                                 |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `swig: No such file or directory`                | not on Lite                                                                                                                                  | `apt install swig`                                                                  |
| `cannot find -llgpio`                            | `lgpio` is only a SWIG binding, the C library is separate                                                                                    | `apt install liblgpio-dev`                                                          |
| `runuser: failed to execute git`                 | Lite ships no git                                                                                                                            | bootstrap installs it                                                               |
| `fatal: $HOME not set`                           | systemd services get almost no environment; `git config --global` and pip's cache both need it                                               | `Environment=HOME=/root`                                                            |
| `Python.h: No such file`                         | no `python3-dev` on Lite                                                                                                                     | added to `install.sh`                                                               |
| No SSH on a flashed card                         | `prepare_image.sh` deleted host keys and relied on `regenerate_ssh_host_keys.service`, which ships with `raspberrypi-sys-mods` - absent here | `prepare_image.sh` writes its own oneshot ordered before `ssh.service`/`ssh.socket` |
| `Some index files failed to download`            | `apt-get update` ran before NTP corrected the clock                                                                                          | retried once                                                                        |
| `Could not resolve host: climatenet-base.img.gz` | libcurl parsed a relative filename as a hostname                                                                                             | absolute `file://` URL                                                              |

---

## What to do next

**Immediate**, in order:

1. Commit the `make_os_list.sh` fix.
2. Retest step 9 - confirm Imager accepts the corrected `file://` URL.
3. Flash a card and boot it **without touching anything**. This is the outstanding
   proof: SSH works immediately, `FirstBootSetup` completes unattended.

**Then:**

4. **Shrink the image.** `extract_size` is 15.9 GB because a 15.9 GB card was
   captured, though Lite uses only ~2-3 GB. The download stays ~730 MB either way, but
   every station card must be ≥16 GB and each flash writes the full 15.9 GB. PiShrink
   on a Linux box cuts it to ~3 GB - roughly five times faster per card. The
   compressed download barely changes, so this is purely about flash time and minimum
   card size.
5. **Publish.** GitHub Releases takes files up to 2 GB. Then regenerate with
   `URL=https://...`, commit `os_list.json`, and point Imager at its raw URL.
6. **Check whether APP OPTIONS persists the repository**, so operators do not need a
   launcher script.
7. **Merge to `main`** - and delete `Environment=BRANCH=custom-rpi-image` from
   `FirstBootSetup.service` when you do.
8. Check the Dependabot alerts GitHub flagged on `main` (7 as of 2026-08-11).

---

## A note on rpi-image-gen

Everything here builds the image by **modifying a running system and copying its SD
card**. That works, but it is imperative and not reproducible: the image is whatever
that one card happened to contain, and rebuilding means repeating the manual steps.

Raspberry Pi's own [`rpi-image-gen`](https://github.com/raspberrypi/rpi-image-gen)
builds images **declaratively** from a config file. Worth evaluating when this resumes,
because it would address the parts that are awkward here:

- Reproducible builds from a checked-in config, instead of a card someone prepared
- No strip step - nothing station-specific ever gets in, so `prepare_image.sh` mostly
  disappears
- Correctly sized images by construction, which removes the PiShrink step entirely
- Native cloud-init and `raspi-config-vendor` support, which is what the Imager dialog
  depends on

The cost is learning its config format and a build host. The trade is roughly: a day
of setup against a build process that never drifts. Given that this image needed four
rebuild cycles to find four missing packages, that trade looks better than it did at
the start.

The older `pi-gen` is the same idea and predates it; `rpi-image-gen` is the current
recommendation.
