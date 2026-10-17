import sys
import paramiko
import time

VPS_IP = "77.83.206.138"
VPS_USER = "root"

def deploy(password: str):
    print(f"Connecting to {VPS_USER}@{VPS_IP}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(VPS_IP, username=VPS_USER, password=password, timeout=10)
        print("Connected successfully!")
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

    cmd = "curl -sSL https://raw.githubusercontent.com/ahmadulloh/anvarsave-bot/main/setup_vps.sh | bash"
    print(f"Executing: {cmd}")
    
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    
    for line in iter(stdout.readline, ""):
        print(line, end="")
        
    exit_status = stdout.channel.recv_exit_status()
    print(f"Deployment finished with exit status: {exit_status}")
    ssh.close()
    return exit_status == 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_to_vps.py <password>")
        sys.exit(1)
    deploy(sys.argv[1])
