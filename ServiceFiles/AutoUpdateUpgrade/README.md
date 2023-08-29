# System Update & Upgrade Service

This unit file defines a service that performs a system update by running the `apt update` and `apt upgrade -y` commands. The service will execute these commands during system startup or when triggered manually. The output of the update process will be logged to a file named update.log on the user's desktop.


## Installation and Usage

1. Open a text editor as the root user (e.g., using `sudo vim /etc/systemd/system/AutoUpdateUpgrade.service`).

2. Copy and paste the unit file contents into the text editor.

3. Modify the `ExecStart` directive to replace username with the actual `username` of the user whose desktop you want to store the **update.log** file. Make sure the path is correct for the user's desktop.

4. Save the file and exit the text editor.

5. Reload the systemd daemon to recognize the new unit:

   ```
   sudo systemctl daemon-reload
   ```
   Enable the service to start on boot:

   ```
   sudo systemctl enable AutoUpdateUpgrade.service
   ```

   Start the service

   ```
   sudo systemctl start AutoUpdateUpgrade.service
   ```

The system will now execute the update commands during the boot process and save the output to the specified `update.log` file on the user's desktop.
