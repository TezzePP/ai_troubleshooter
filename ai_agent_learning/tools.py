import subprocess


def get_server_status(server):
    result = subprocess.run(
        ["ping", "-n", "1", server],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return f"Server {server} is reachable."

    return f"Server {server} is not reachable."

def get_disk_space():
    return "The server has 120 GB of free disk space."

def get_ssh_port_status():
    return "SSH port 22 is closed."