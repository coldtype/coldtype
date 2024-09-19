from pathlib import Path

from coldtype.renderer.utils import path_hash
from coldtype.renderer.winman.passthrough import WinmanPassthrough
from coldtype.blender.render import blender_launch_livecode
from coldtype.blender import BlenderIO



class WinmanBlender(WinmanPassthrough):
    def __init__(self, config):
        self.subp = None
        self.command_file = None

        try:
            from b3denv import get_vars
            b3d_vars = get_vars(None)
            self.blender_path = Path(b3d_vars["blender"])
        except:
            raise Exception("NO BLENDER FOUND (via b3denv)")

        self.reset_factory = config.blender_reset_factory
        self.cli_args = config.blender_command_line_args
    
    def launch(self, blender_io:BlenderIO):
        if self.subp:
            self.subp.kill()

        self.subp = blender_launch_livecode(
            self.blender_path,
            blender_io.blend_file,
            self.command_file,
            #reset_factory=self.reset_factory,
            additional_args=self.cli_args)
    
    def write_command(self, cmd, arg, kwargs=[]):
        try:
            cb = self.command_file
            if cb.exists():
                cb.unlink()
            cb.write_text(f"{cmd},{str(arg)};{str(kwargs)}")
        except FileNotFoundError:
            pass

    def did_render(self, count, ditto_last, renders):
        if ditto_last:
            self.write_command("refresh_sequencer_and_image", count)
        else:
            self.write_command("refresh_sequencer", count)
    
    def reload(self, filepath, source_reader):
        ph = path_hash(filepath)
        self.command_file = Path(f"~/.coldtype/{ph}.txt").expanduser()
        self.write_command("import", filepath, source_reader.inputs)
    
    def toggle_playback(self, toggle):
        self.write_command("play_preview", toggle)
    
    def frame_offset(self, offset):
        self.write_command("frame_offset", offset)

    def terminate(self):
        if self.subp:
            self.subp.kill()