import socket, subprocess, os, signal
from pathlib import Path

try:
    import livereload
except ImportError:
    print("> pip install livereload")


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def maybe_run_server(livereload:bool, port:int, dir:Path):
    if not is_port_in_use(port):
        if livereload:
            os.system(" ".join(["livereload", "-p", str(port), str(dir), "&>/dev/null", "&"]))
        else:
            os.system(f"python -m http.server {port} -d {dir} &>/dev/null &")
        return True
    else:
        return False


def kill_process_on_port_unix(port):
    os.system(f"lsof -i tcp:{port} | awk 'NR!=1 {{print $2}}' | xargs kill")


