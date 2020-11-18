from enum import Enum
from pathlib import Path
import json, glfw, skia, re
from coldtype import hsl, Action, Keylayer, Point


class RendererStateEncoder(json.JSONEncoder):
    def default(self, o):
        return {
            "controller_values": o.controller_values
        }


class Mods():
    def __init__(self):
        self.reset()
    
    def update(self, mods):
        if mods & glfw.MOD_SUPER:
            self.super = True
        if mods & glfw.MOD_SHIFT:
            self.shift = True
        if mods & glfw.MOD_ALT:
            self.alt = True
        if mods & glfw.MOD_CONTROL:
            self.ctrl = True
    
    def reset(self):
        self.super = False
        self.shift = False
        self.ctrl = False
        self.alt = False
    
    def __repr__(self):
        return f"su:{self.super};sh:{self.shift};alt:{self.alt};ctrl:{self.ctrl}"


class RendererState():
    def __init__(self, renderer):
        self.renderer = renderer
        self.previewing = False
        self.preview_scale = 1
        self.controller_values = {}
        self.keylayer_shifting = False
        self.keylayer = Keylayer.Default
        self.keybuffer = []
        #self.needs_display = 0
        self.request = None
        self.cmd = None
        self.arrow = None
        self.mods = Mods()
        self.mouse = None
        self.mouse_down = False
        self.xray = True
        self.selection = [0]
        self.zoom = 1
        self.frame_index_offset = 0
        self.canvas = None
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
    
    def on_mouse_button(self, pos, btn, action, mods):
        self.mods.update(mods)
        if action == glfw.PRESS:
            self.mouse_down = True
            self.mouse = pos.scale(1/self.preview_scale)
            return Action.PreviewStoryboard
        elif action == glfw.RELEASE:
            self.mouse_down = False
            new_mouse = pos.scale(1/self.preview_scale)
            if self.mouse:
                if new_mouse.x != self.mouse.x and new_mouse.y != self.mouse.y:
                    return Action.PreviewStoryboard

    def on_mouse_move(self, pos):
        if self.mouse_down:
            pos = pos.scale(1/self.preview_scale)
            if self.mouse:
                if abs(pos.x - self.mouse.x) > 5 or abs(pos.y - self.mouse.y) > 5:
                    self.mouse = pos
                    return Action.PreviewStoryboard
    
    def on_character(self, codepoint):
        cc = chr(codepoint)
        if self.keylayer == Keylayer.Cmd:
            self.keybuffer.append(cc)
            return Action.PreviewStoryboard
        elif self.keylayer == Keylayer.Editing:
            if cc == "f":
                return
            if re.match(r"[1-9]{1}", cc):
                self.zoom = int(cc)
            elif cc == "=":
                self.zoom += 0.25
            elif cc == "-":
                self.zoom -= 0.25
            #else:
            #    self.cmd = cc
            self.zoom = max(0.25, min(10, self.zoom))
            return Action.PreviewStoryboard
        #self.needs_display = 1
    
    def on_key(self, win, key, scan, action, mods):
        if action != glfw.PRESS and action != glfw.REPEAT:
            return
        
        self.mods.update(mods)
        
        if key == glfw.KEY_ENTER:
            cmd = "".join(self.keybuffer)
            self.cmd = cmd
            self.keybuffer = []
            #print(">>> KB-CMD:", cmd)
            self.exit_keylayer()
            return Action.PreviewStoryboard
        elif key == glfw.KEY_BACKSPACE:
            if len(self.keybuffer) > 0:
                self.keybuffer = self.keybuffer[:-1]
                return Action.PreviewStoryboard
        elif key == glfw.KEY_ESCAPE:
            self.exit_keylayer()
            return Action.PreviewStoryboard

        elif self.keylayer == Keylayer.Editing:
            if key == glfw.KEY_D:
                self.exit_keylayer()
                return Action.PreviewStoryboard
            elif key in [glfw.KEY_UP, glfw.KEY_DOWN, glfw.KEY_LEFT, glfw.KEY_RIGHT]:
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
            elif key == glfw.KEY_E and self.keylayer == Keylayer.Editing:
                self.exit_keylayer()
                return Action.PreviewStoryboard
            elif key == glfw.KEY_F and self.keylayer == Keylayer.Editing:
                self.xray = not self.xray
                return Action.PreviewStoryboard
        
        if key == glfw.KEY_S and mods & glfw.MOD_SUPER:
            self.cmd = "save"
            return Action.PreviewStoryboard
        return
    
    def exit_keylayer(self):
        self.keylayer = Keylayer.Default
        self.keybuffer = []
    
    def draw_keylayer(self, canvas, rect, typeface):
        canvas.save()
        if self.keylayer == Keylayer.Cmd:
            canvas.drawRect(skia.Rect.MakeXYWH(0, rect.h-50, rect.w, 50), skia.Paint(AntiAlias=True, Color=hsl(0.9, l=0.25, a=0.85).skia()))
            canvas.drawString("".join(self.keybuffer), 10, rect.h-14, skia.Font(typeface, 30), skia.Paint(AntiAlias=True, Color=skia.ColorWHITE))
        elif self.keylayer == Keylayer.Editing:
            canvas.drawRect(skia.Rect(0, 0, 50, 50), skia.Paint(AntiAlias=True, Color=hsl(0.95, l=0.5, a=0.75).skia()))
        canvas.restore()
    
    def increment_selection(self, amount, limit):
        if len(self.selection) == 1:
            if amount == 0:
                return
            si = self.selection[0]
            si += amount
            if si >= limit:
                si = 0
            elif si < 0:
                si = limit - 1
            self.selection[0] = si
        else:
            print("invalid")
    
    def reset_keystate(self):
        self.cmd = None
        self.arrow = None
        self.mods.reset()
        #self.mouse = None