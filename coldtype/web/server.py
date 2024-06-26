import socket, subprocess, os, signal


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def kill_process_on_port_unix(port):
    os.system(f"lsof -i tcp:{port} | awk 'NR!=1 {{print $2}}' | xargs kill")
    # result = subprocess.run(['lsof', '-i', f':{port}'], capture_output=True, text=True)
    # print(result.returncode)
    # print(result.stdout)
    # if result.returncode == 0:
    #     lines = result.stdout.strip().split('\n')
    #     for line in lines:
    #         if line.startswith("Python"):
    #             pid = int(lines[1].split()[1])
    #             print(f"Found PID {pid} using port {port}")
    #             print(os.kill(pid, signal.SIGTERM))


