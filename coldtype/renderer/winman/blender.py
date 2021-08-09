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
    
    def reload(self, filepath):
        try:
            cb = Path("~/.coldtype/blender.txt").expanduser()
            if cb.exists():
                cb.unlink()
            cb.write_text(f"import,{str(filepath)}")
        except FileNotFoundError:
            pass

    def terminate(self):
        if self.subp:
            self.subp.kill()