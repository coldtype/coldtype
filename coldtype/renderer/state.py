from pathlib import Path
import json, glfw, skia
from coldtype import hsl, Action


class RendererStateEncoder(json.JSONEncoder):
    def default(self, o):
        return {
            "controller_values": o.controller_values
        }


class RendererState():
    def __init__(self, renderer):
        self.renderer = renderer
        self.previewing = False
        self.preview_scale = 1
        self.controller_values = {}
        self.keylayer = 0
        self.keybuffer = []
        #self.needs_display = 0
        self.cmd = None
        self.arrow = None
        self.reset()
    
    def reset(self):
        if self.filepath:
            try:
                deserial = json.loads(self.filepath.read_text())
                cv = deserial.get("controller_values")
                if cv:
                    self.controller_values = cv
            except json.decoder.JSONDecodeError:
                self.controller_values = {}
            except FileNotFoundError:
                self.controller_values = {}
    
    def clear(self):
        if self.filepath:
            self.filepath.write_text("")
        self.reset()
    
    @property
    def filepath(self):
        if self.renderer.filepath:
            return Path(str(self.renderer.filepath).replace(".py", "") + "_state.json")
        else:
            return None
    
    @property
    def midi(self):
        return self.controller_values
    
    def persist(self):
        if self.filepath:
            print("Saving Controller State...")
            self.filepath.write_text(RendererStateEncoder().encode(self))
        else:
            print("No source; cannot persist state")
    
    def on_character(self, codepoint):
        if self.keylayer < 0:
            self.keylayer = abs(self.keylayer)
        elif self.keylayer > 0:
            self.keybuffer.append(chr(codepoint))
            return Action.PreviewStoryboard
        #self.needs_display = 1
    
    def on_key(self, win, key, scan, action, mods):
        if action != glfw.PRESS and action != glfw.REPEAT:
            return
        
        if key == glfw.KEY_ENTER:
            cmd = "".join(self.keybuffer)
            self.cmd = cmd
            self.keybuffer = []
            print(">>> KB-CMD:", cmd)
            #self.needs_display = 1
            return Action.PreviewStoryboard
        elif key == glfw.KEY_BACKSPACE:
            if len(self.keybuffer) > 0:
                self.keybuffer = self.keybuffer[:-1]
                #self.needs_display = 1
                return Action.PreviewStoryboard

        elif key == glfw.KEY_ESCAPE:
            print("EXITING KEYBUFFER")
            self.keylayer = 0
            self.keybuffer = []
            return Action.PreviewStoryboard
            #self.needs_display = 1
        elif key in [glfw.KEY_UP, glfw.KEY_DOWN, glfw.KEY_LEFT, glfw.KEY_RIGHT]:
            if self.keylayer == 2:
                if key == glfw.KEY_UP:
                    self.arrow = [0, 1]
                elif key == glfw.KEY_DOWN:
                    self.arrow = [0, -1]
                elif key == glfw.KEY_LEFT:
                    self.arrow = [-1, 0]
                elif key == glfw.KEY_RIGHT:
                    self.arrow = [1, 0]
                if mods & glfw.MOD_SHIFT:
                    for idx, a in enumerate(self.arrow):
                        self.arrow[idx] = a * 10
                return Action.PreviewStoryboard
        return
    
    def draw_keylayer(self, canvas, rect):
        canvas.save()
        if self.keylayer == 1:
            canvas.drawRect(skia.Rect(0, 0, rect.w, 50), skia.Paint(AntiAlias=True, Color=hsl(0.95, l=0.5, a=0.5).skia()))
            canvas.drawString("".join(self.keybuffer), 10, 32, skia.Font(None, 30), skia.Paint(AntiAlias=True, Color=skia.ColorWHITE))
        elif self.keylayer == 2:
            canvas.drawRect(skia.Rect(0, 0, 50, 50), skia.Paint(AntiAlias=True, Color=hsl(0.95, l=0.5, a=0.75).skia()))
        canvas.restore()
    
    def reset_keystate(self):
        self.cmd = None
        self.arrow = None