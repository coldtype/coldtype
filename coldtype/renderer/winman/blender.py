from pathlib import Path

from coldtype.renderer.utils import path_hash
from coldtype.renderer.winman.passthrough import WinmanPassthrough
from coldtype.blender.render import blender_launch_livecode
from coldtype.blender import BlenderIO

class WinmanBlender(WinmanPassthrough):
    def __init__(self, config):
        self.subp = None
        self.command_file = None
        self.blender_app_path = config.blender_app_path
        print("BLENDER APP PATH>", self.blender_app_path)
    
    def launch(self, blender_io:BlenderIO):
        if self.subp:
            self.subp.kill()
        self.subp = blender_launch_livecode(
            self.blender_app_path,
            blender_io.blend_file,
            self.command_file)
    
    def write_command(self, cmd, arg):
        try:
            cb = self.command_file
            if cb.exists():
                cb.unlink()
            cb.write_text(f"{cmd},{str(arg)}")
        except FileNotFoundError:
            pass

    def did_render(self, count, ditto_last):
        if ditto_last:
            self.write_command("refresh_sequencer_and_image", count)
        else:
            self.write_command("refresh_sequencer", count)
    
    def reload(self, filepath):
        ph = path_hash(filepath)
        self.command_file = Path(f"~/.coldtype/{ph}.txt").expanduser()
        self.write_command("import", filepath)
    
    def toggle_playback(self, toggle):
        self.write_command("play_preview", toggle)
    
    def frame_offset(self, offset):
        self.write_command("frame_offset", offset)

    def terminate(self):
        if self.subp:
            self.subp.kill()