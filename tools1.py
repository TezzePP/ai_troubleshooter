import subprocess


def ping_host(host: str) -> str:
    """Check whether a host responds to ping."""

    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "2000", host],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            return f"Host {host} responded to ping."

        return f"Host {host} did not respond to ping."

    except Exception as e:
        return f"Ping failed: {e}"


def check_ssh_port(host: str) -> str:
    """Check whether TCP port 22 is open."""

    try:
        result = subprocess.run(
            [
                "powershell",
                "-Command",
                f"Test-NetConnection -ComputerName {host} -Port 22"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if "TcpTestSucceeded : True" in result.stdout:
            return f"SSH port 22 on {host} is OPEN."

        return f"SSH port 22 on {host} is CLOSED or unreachable."

    except Exception as e:
        return f"Port check failed: {e}"


def check_ssh_service() -> str:
    """Check whether the local SSH service is running."""

    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-Service sshd"],
            capture_output=True,
            text=True,
            timeout=5
        )

        return result.stdout

    except Exception as e:
        return f"SSH service check failed: {e}"
    


