import subprocess

# Function to get the network interface currently in use
def get_network_interface():
    result = subprocess.run("route | grep '^default' | grep -o '[^ ]*$'", shell=True, capture_output=True, text=True)
    output = result.stdout
    
    lines = output.split('\n')
    
    return lines[0] if lines[0] else False


# Function to check if the system is connected to a network
def is_connected():
    interface = get_network_interface()

    if interface:
        return True
    else:
        return False