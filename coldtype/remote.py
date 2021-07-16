import json
from pathlib import Path

def remote(command):
    (Path("~/.coldtype/command.json")
        .expanduser()
        .write_text(json.dumps(dict(action=command if isinstance(command, str) else command.value))))

def show_picklejar():
    remote("reload_source")

if __name__ == "__main__":
    remote("play_preview")