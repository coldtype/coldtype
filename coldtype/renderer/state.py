from enum import Enum
from pathlib import Path
import json, re, base64
from coldtype import hsl, Action, Keylayer, Point, Rect, DATPen, Overlay
from typing import Callable, List
from time import sleep

try:
    import skia
except ImportError:
    skia = None

try:
    import glfw
except ImportError:
    glfw = None

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


class InputHistoryItem():
    def __init__(self, position, action, keylayer, midi):
        self.position = position
        self.action = action
        self.keylayer = keylayer
        self.midi = midi
        self.idx = -1
    
    def __repr__(self):
        return f"InputHistoryItem({self.idx}/{self.action}/{self.position})"


class InputHistoryGroup():
    def __init__(self, action, keylayer, items):
        self.action = action
        self.keylayer = keylayer
        self.items = []
    
    def append(self, item):
        self.items.append(item)
    
    def __len__(self):
        return len(self.items)
    
    def __getitem__(self, index):
        return self.items[index]
    
    def position(self):
        if len(self.items) > 0:
            return self.items[0].position
    
    def start(self):
        if len(self.items) > 0:
            return self.items[0].idx
    
    def end(self):
        if len(self.items) > 0:
            return self.items[-1].idx
    
    def __repr__(self):
        return f"InputHistoryGroup:{self.action}:{self.start()}-{self.end()}"


class InputHistory():
    def __init__(self):
        self.history = []

    def clear(self) -> bool:
        """Return True if something was cleared"""
        if len(self.history) > 0:
            self.history = []
            return True
        else:
            self.history = []
            return False
    
    def empty(self):
        return len(self.history) == 0
    
    def record(self, item:InputHistoryItem):
        item.idx = len(self.history)
        self.history.append(item)
    
    def last(self, action=None) -> InputHistoryItem:
        for i in reversed(self.history):
            if not action:
                return i
            elif i.action == action:
                return i
            elif callable(action):
                if action(i.action):
                    return i
    
    def undo(self):
        strokes = self.strokes()
        if strokes:
            last_stroke = strokes[-1]
            self.history = self.history[:last_stroke.start()]
    
    def strokes(self, filterfn:Callable[[InputHistoryGroup], bool]=lambda g: True) -> List[InputHistoryGroup]:
        xs = []
        for i in self.history:
            if i.action == "down":
                xs.append(InputHistoryGroup("down", i.keylayer, []))
            elif i.action == "up":
                xs.append(InputHistoryGroup("up", i.keylayer, []))
            elif i.action == "cmd":
                xs.append(InputHistoryGroup("cmd", i.keylayer, []))
            
            if len(xs) == 0 and i.action == "move":
                continue
            else:
                xs[-1].append(i)
        return [x for x in xs if filterfn(x)]
    
    def downstrokes(self):
        return self.strokes(lambda g: g.action == "down")
    
    def upstrokes(self):
        return self.strokes(lambda g: g.action == "up")
    
    def moved(self) -> bool:
        last_down = self.last("down")
        last_up = self.last("up")
        if last_down and last_up and last_down.idx < last_up.idx:
            return last_down.position != last_up.position
        return False
    
    def __getitem__(self, index):
        if len(self.history) > 0:
            return self.history[index]


class RendererState():
    def __init__(self, renderer):
        self.renderer = renderer
        self.previewing = False
        self.preview_scale = 1
        self.controller_values = {}
        self.keylayer_shifting = False
        self.keylayer = Keylayer.Default
        self.keybuffer = []
        self.overlays = {}
        #self.needs_display = 0
        self.request = None
        self.callback = None
        self.cmd = None
        self.text = ""
        self.clear_text = False
        self.arrow = None
        self.mods = Mods()
        self.record_mouse_moves = True
        self.input_history:InputHistory = InputHistory()
        self.xray = True
        self.selection = [0]
        self.zoom = 1
        self._frame_offsets = {}
        self._initial_frame_offsets = {}
        self.canvas = None
        self._last_filepath = None
        self.watch_soft_mods = {}
        self.watch_mods = {}
        self.external_url = None
        self.reset()
    
    def reset(self, ignore_current_state=False):
        if self.filepath == self._last_filepath and not ignore_current_state:
            return
        
        if self.filepath:
            self._last_filepath = self.filepath
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
    
    def record_mouse(self, pos, action):
        new_mouse = pos.scale(1/self.preview_scale)
        self.input_history.record(
            InputHistoryItem(new_mouse, action, self.keylayer, self.controller_values.copy()))
        if action == "down":
            return Action.PreviewStoryboard
        elif action == "up" and self.input_history.moved():
            return Action.PreviewStoryboard
        elif action == "move" and self.keylayer == Keylayer.Editing:
            return Action.PreviewStoryboard
    
    def on_mouse_button(self, pos, btn, action, mods):
        if btn == 1 and action == glfw.PRESS:
            self.input_history.clear()
            return Action.PreviewStoryboard
        
        self.mods.update(mods)
        if action == glfw.PRESS:
            return self.record_mouse(pos, "down")
        elif action == glfw.RELEASE:
            return self.record_mouse(pos, "up")
    
    def on_mouse_move(self, pos):
        if self.record_mouse_moves:
            return self.record_mouse(pos, "move")
    
    @property
    def mouse_history(self):
        strokes = self.input_history.downstrokes()
        strokes = [[p.position for p in s.items] for s in strokes]
        return strokes
    
    @property
    def mouse_down(self):
        strokes = self.input_history.strokes()
        if len(strokes) > 0 and strokes[-1][0] == "down":
            return True
        else:
            return False
    
    @property
    def mouse(self):
        item = self.input_history.last(lambda a: a in ["up", "down", "move"])
        if item:
            return item.position
    
    def mod_preview_scale(self, inc, absolute=0):
        if absolute > 0:
            ps = absolute
        else:
            ps = self.preview_scale + inc
        self.preview_scale = max(0.1, min(5, ps))
    
    def shape_selection(self):
        # TODO could be an arbitrary lasso-style thing?
        if self.mouse_history:
            start = self.mouse_history[-1][0]
            end = self.mouse_history[-1][-1]
            rect = Rect.FromPoints(start, end)
            return DATPen().rect(rect)
        
    def polygon_selection(self, clear_on="save"):
        mh = self.mouse_history
        if not mh:
            return False, DATPen()
        
        polygon = DATPen()
        polygon.line([m[-1] for m in mh])
        polygon.f(None).s(hsl(0.75, s=1, a=0.5)).sw(5)
        #polygon.closePath()

        if self.cmd == clear_on:
            self.input_history.clear()
            return True, polygon
        else:
            return False, polygon
    
    def on_character(self, codepoint):
        cc = chr(codepoint)
        if self.keylayer == Keylayer.Cmd or self.keylayer == Keylayer.Text:
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
            if self.keylayer == Keylayer.Cmd:
                self.cmd = cmd
            elif self.keylayer == Keylayer.Text:
                self.text = cmd
            self.keybuffer = []
            #print(">>> KB-CMD:", cmd)
            if mods & glfw.MOD_SUPER:
                # keep editing
                pass
            else:
                self.exit_keylayer()
            return Action.PreviewStoryboard
        elif key == glfw.KEY_BACKSPACE:
            if len(self.keybuffer) > 0:
                self.keybuffer = self.keybuffer[:-1]
                return Action.PreviewStoryboard
        elif key == glfw.KEY_ESCAPE:
            if self.keylayer == Keylayer.Editing:
                cleared = self.input_history.clear()
                if cleared:
                    return Action.PreviewStoryboard
            
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
            elif key == glfw.KEY_Z and self.keylayer == Keylayer.Editing:
                self.input_history.undo()
                return Action.PreviewStoryboard
            elif key == glfw.KEY_B and self.keylayer == Keylayer.Editing:
                self.input_history.record(InputHistoryItem(key, "cmd", self.keylayer, self.controller_values.copy()))
            elif key == glfw.KEY_C and self.keylayer == Keylayer.Editing:
                self.input_history.record(InputHistoryItem(key, "cmd", self.keylayer, self.controller_values.copy()))

        
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
            canvas.drawRect(
                skia.Rect.MakeXYWH(0, rect.h-50, rect.w, 50),
                skia.Paint(
                    AntiAlias=True,
                    Color=hsl(0.9, l=0.25, a=0.85).skia()))
            canvas.drawString(
                "".join(self.keybuffer),
                10,
                rect.h-14,
                skia.Font(typeface, 30),
                skia.Paint(
                    AntiAlias=True,
                    Color=skia.ColorWHITE))
        
        elif self.keylayer == Keylayer.Text:
            canvas.drawRect(
                skia.Rect.MakeXYWH(0, 0, rect.w, 50),
                skia.Paint(
                    AntiAlias=True,
                    Color=hsl(0.7, l=0.25, a=0.85).skia()))
            canvas.drawString(
                "".join(self.keybuffer),
                10,
                34,
                skia.Font(typeface, 30),
                skia.Paint(
                    AntiAlias=True,
                    Color=skia.ColorWHITE))
        
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
    
    def add_frame_offset(self, key, offset):
        if key in self._frame_offsets:
            offsets = self._frame_offsets[key]
            initials = self._initial_frame_offsets[key]
            offsets.append(offset)
            initials.append(offset)
        else:
            self._frame_offsets[key] = [offset]
            self._initial_frame_offsets[key] = [offset]
    
    def get_frame_offsets(self, key):
        return self._frame_offsets.get(key, [0])
    
    def adjust_all_frame_offsets(self, adj, absolute=False):
        if absolute:
            for k, v in self._frame_offsets.items():
                for i, o in enumerate(v):
                    v[i] = adj
        else:
            for k, v in self._frame_offsets.items():
                for i, o in enumerate(v):
                    v[i] = o + adj
    
    def adjust_keyed_frame_offsets(self, key, fn):
        offs = self.get_frame_offsets(key)
        for i, o in enumerate(offs):
            offs[i] = fn(i, o)
    
    def read_text(self, clear=False):
        self.clear_text = clear
        if self.keybuffer:
            return "".join(self.keybuffer)
        elif self.text:
            return self.text
        else:
            return None
    
    def reset_keystate(self):
        self.cmd = None
        if self.clear_text:
            self.text = ""
            self.clear_text = False
        self.arrow = None
        self.mods.reset()
        self.watch_mods = {}
        self.watch_soft_mods = {}
    
    def toggle_overlay(self, overlay):
        v = not self.overlays.get(overlay, False)
        if not v:
            if overlay in self.overlays:
                del self.overlays[overlay]
        else:
            self.overlays[overlay] = True
    
    def notify_external(self, idx):
        from websocket import create_connection
        ws = None
        try:
            ws = create_connection(self.external_url)
            print("> open", idx)
            ws.send(json.dumps({"rendered": idx}))
        except ConnectionRefusedError:
            print("!!! Could not connect to websocket", self.external_url)
        if ws:
            print("< close", idx)
            ws.close()
        return self