from pathlib import Path

FFMPEG_COMMAND = "ffmpeg"

def set_ffmpeg_command(cmd):
    if "/" in cmd:
        cmd = str(Path(cmd).expanduser().absolute())

    global FFMPEG_COMMAND
    FFMPEG_COMMAND = cmd