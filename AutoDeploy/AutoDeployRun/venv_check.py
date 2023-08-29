import os

def check_venv_folder():
    venv_path = "/home/ubuntu/workspace/Test/venv"
    
    if os.path.exists(venv_path) and os.path.isdir(venv_path):
        return True
    else:
        os.system("python3 -m venv venv")
        os.system("venv/bin/python -m pip install -r requirements.txt")

if __name__ == "__main__":
    check_venv_folder()
