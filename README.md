Follow these steps carefully for the initial setup of your Raspberry Soft application.

## Initial Setup

**Important:**
- Ensure that the username for your Raspberry Pi is set to `raspberry`.
- The last tested and stable version for this application is Raspberry Pi OS (Legacy, 32-bit) Debian Bullseye. You can download it from [this link](https://downloads.raspberrypi.com/raspios_oldstable_armhf/images/raspios_oldstable_armhf-2024-03-12/).

1. **Install `vim` on your Raspberry Pi:**
   ```bash 
   sudo apt update
   sudo apt install vim
   ```
2. **Create a workspace directory:**
    ```bash
    mkdir /home/raspberry/workspace
    cd /home/raspberry/workspace
    ```

3. **Clone the repository:**
    ```bash
    git clone https://github.com/ClimateNetTumoLabs/raspberry_soft.git
    cd raspberry_soft/app
    ```
4. **Checkout to current working branch:**
    ```bash
   git checkout full-rewrite
   ```
5. **Configure the environment variables:**
   Copy `env_template` to `.env` and update the values, including the
 `DEVICE_ID` and `MQTT_BROKER_ENDPOINT`
   ```bash 
   cp env_template .env
   vim .env
   ```

6. **Add your Wi-Fi credentials:**
   Update the SSID and password in `config.py`.
   ```bash
   vim config.py
   ```

7. **Copy the AWS IoT Core certificates from your LOCAL computer's terminal:**
    Copy the certificate files (`certificate.pem.crt`, `private.pem.key`, `public.pem.key`, `rootCA.pem`) into the `/home/raspberry/workspace/raspberry_soft/app/data/utils/` directory:   
If you have not created certificates, follow this [link](https://github.com/ClimateNetTumoLabs/raspberry_soft/wiki/Creating-IoT-Core-Thing)
   
   ```bash
   scp -r <folder_path>/certificates/ <username>@<IP>:/home/raspberry/workspace/raspberry_soft/app/utils/
   ```

8. **Run the installation script:**
   Run the installation script with `sudo` privilage:
   ```bash
   cd /home/raspberry/workspace/raspberry_soft/
   chmod +x install.sh
   sudo ./install.sh
   ```

9. **Reboot the system:**
   ```bash
   sudo reboot
   ```

10. **Test the functionality of the device:**
    Combine the sensors, pcb, fully make the device, activate the virtual environment and run the `testing.py` program:
    ```bash
    cd /home/raspberry/workspace/raspberry_soft/app/
    source venv/bin/activate
    python testing.py
    ```
