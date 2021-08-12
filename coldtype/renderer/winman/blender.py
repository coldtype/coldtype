from pathlib import Path

from coldtype.renderer.winman.passthrough import WinmanPassthrough
from coldtype.blender.render import blender_launch_livecode

class WinmanBlender(WinmanPassthrough):
    def __init__(self):
        pass
        self.subp = None
    
    def launch(self, blend_file):
        if self.subp:
            self.subp.kill()
        self.subp = blender_launch_livecode(blend_file)
    
    def write_command(self, cmd, arg):
        try:
            cb = Path("~/.coldtype/blender.txt").expanduser()
            if cb.exists():
                cb.unlink()
            cb.write_text(f"{cmd},{str(arg)}")
        except FileNotFoundError:
            pass
    
    def reload(self, filepath):
        self.write_command("import", filepath)
    
    def toggle_playback(self, toggle):
        self.write_command("play_preview", toggle)
    
    def frame_offset(self, offset):
        self.write_command("frame_offset", offset)

    def terminate(self):
        if self.subp:
            self.subp.kill()