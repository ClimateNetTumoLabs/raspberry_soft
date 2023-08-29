# Automatic Installation of Service Files

The code will clone a Git repository, set up and start two systemd services (`AutoUpdateUpgrade.service` and `InetCheckConnect.service`), and then clean up by removing the cloned directory.

## Installation and Usage

1. Save the `install.sh` on your computer.

2. Give execute permission with command

   ```
   chmod +x install.sh
   ```

3. Run the script with command

   ```
   ./install.sh
   ```
