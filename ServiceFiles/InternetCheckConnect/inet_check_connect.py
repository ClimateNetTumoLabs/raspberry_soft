import subprocess
from time import sleep
from datetime import datetime


# Known Wi-Fi networks and their corresponding passwords
known_wifi = {
    "SSID": "PASSWORD"
}


# Function to get the IP address of the system
def get_ip():
    ip_result = subprocess.run(f"hostname -I", shell=True, capture_output=True, text=True)
    ip = ip_result.stdout
    return ip


# Function to get a list of available Wi-Fi networks
def get_wifi_networks():
    command = "sudo iwlist scan | grep 'ESSID'"
    
    # Retry up to 3 times in case of failure
    for i in range(3):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output_lines = result.stdout.split("\n")

        wifi_networks = [line.split(":")[1].strip(' "') for line in output_lines if line]
        
        if wifi_networks:
            break
        
        sleep(1)
        
    return wifi_networks


# Function to connect to a Wi-Fi network
def connect_to_wifi(ssid):
    if ssid in known_wifi:
        command = f"nmcli device wifi connect '{ssid}' password '{known_wifi[ssid]}'"

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout

        return True if "successfully activated" in output else False
    else:
        return False


# Function to get the network interface currently in use
def get_network_interface():
    result = subprocess.run("route | grep '^default' | grep -o '[^ ]*$'", shell=True, capture_output=True, text=True)
    output = result.stdout
    
    lines = output.split('\n')
    
    return lines[0] if lines[0] else False


# Function to get the type of connection (Wi-Fi or LAN)
def get_connection_type(interface):
    result = subprocess.run(f"iwconfig {interface}", shell=True, capture_output=True, text=True)
    output = result.stdout
    
    return 'Wi-Fi' if 'ESSID' in output else 'LAN'


# Function to check if the system is connected to a network
def is_connected():
    interface = get_network_interface()

    if interface:
        connection_type = get_connection_type(interface)
        
        print("Interface:", interface)
        print("Connection Type:", connection_type)
        print("Local Ip Address:", get_ip())
        
        return True
    else:
        print("Not Connected!")
        print("-" * 10) 
        return False


def main():
    print("#" * 10, datetime.now(), "#" * 100)

    # Check if already connected to a network
    if not is_connected():
        # Get a list of available Wi-Fi networks
        ssids = get_wifi_networks()
            
        if not ssids:
            print("No available WiFi networks")
        else:
            for ssid in ssids:
                connected = connect_to_wifi(ssid)
                
                if connected:
                    print("-" * 10)
                    print("Connected to Wi-Fi network:", ssid)
                    print("Local Ip Address:", get_ip())
                    print()
                    break
                else:
                    print("Failed to connect to Wi-Fi network:", ssid)
    print()


if __name__ == "__main__":
    main()

