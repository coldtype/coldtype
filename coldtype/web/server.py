import socket, subprocess, os, signal


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def kill_process_on_port_unix(port):
    result = subprocess.run(['lsof', '-i', f':{port}'], capture_output=True, text=True)
    #print(result)
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if line.startswith("Python") or True:
                pid = int(lines[1].split()[1])
                #print(f"Found PID {pid} using port {port}")
                os.kill(pid, signal.SIGTERM)


