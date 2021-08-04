try:
    import glfw
except ImportError:
    glfw = None

from coldtype.renderer.config import ConfigOption, ColdtypeConfig
from coldtype.renderer.state import Keylayer, Action
from coldtype.geometry import Point

class WindowManagerPassthrough():
    def __init__(self):
        pass

    def set_title(self, text):
        print("TITLE", text)


class WindowManager():
    def __init__(self, config:ColdtypeConfig, renderer, background=False):
        self.config = config
        self.window = None
        self.background = background
        self.renderer = renderer

        self.prev_scale = 0

        if not self.background:
            self.window = glfw.create_window(int(10), int(10), '', None, None)
        
        self.window_scrolly = 0
        self.window_focus = 0

        glfw.make_context_current(self.window)

        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_char_callback(self.window, self.on_character)
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(self.window, self.on_mouse_move)
        glfw.set_scroll_callback(self.window, self.on_scroll)
        glfw.set_window_focus_callback(self.window, self.on_focus)

        self.set_window_opacity()

    def get_content_scale(self):
        u_scale = self.config.window_content_scale
        
        if u_scale:
            return u_scale
        elif glfw and not self.renderer.args.no_viewer:
            if self.renderer.primary_monitor:
                return glfw.get_monitor_content_scale(self.renderer.primary_monitor)[0]
            else:
                return glfw.get_window_content_scale(self.window)[0]
        else:
            return 1
    
    def set_title(self, text):
        glfw.set_window_title(self.window, text)

    def set_window_opacity(self, relative=None, absolute=None):
        if relative is not None:
            o = glfw.get_window_opacity(self.window)
            op = o + float(relative)
        elif absolute is not None:
            op = float(absolute)
        else:
            op = float(self.config.window_opacity)
        
        glfw.set_window_opacity(self.window,
            max(0.1, min(1, op)))
    
    def reset(self):
        self.window_scrolly = 0
    
    def allow_mouse(self):
        return True
        #return self.state.keylayer == Keylayer.Editing
        
    def on_scroll(self, win, xoff, yoff):
        self.window_scrolly += yoff
        #self.on_action(Action.PreviewStoryboard)
        #print(xoff, yoff)
        #pass # TODO!
    
    def on_focus(self, win, focus):
        self.window_focus = focus
    
    def on_mouse_button(self, _, btn, action, mods):
        if not self.allow_mouse():
            return
        
        pos = Point(glfw.get_cursor_pos(self.window)).scale(2) # TODO should this be preview-scale?
        pos[1] = self.renderer.last_rect.h - pos[1]
        requested_action = self.renderer.state.on_mouse_button(pos, btn, action, mods)
        if requested_action:
            self.renderer.action_waiting = requested_action
    
    def on_mouse_move(self, _, xpos, ypos):
        if not self.allow_mouse():
            return
        
        pos = Point((xpos, ypos)).scale(2)
        pos[1] = self.renderer.last_rect.h - pos[1]
        requested_action = self.renderer.state.on_mouse_move(pos)
        if requested_action:
            self.renderer.action_waiting = requested_action
    
    def on_character(self, _, codepoint):
        if self.renderer.state.keylayer != Keylayer.Default:
            if self.renderer.state.keylayer_shifting:
                self.renderer.state.keylayer_shifting = False
                self.renderer.on_action(Action.PreviewStoryboard)
                return
            requested_action = self.renderer.state.on_character(codepoint)
            if requested_action:
                self.renderer.action_waiting = requested_action
    
    def on_key(self, win, key, scan, action, mods):
        if self.renderer.state.keylayer != Keylayer.Default:
            requested_action = self.renderer.state.on_key(win, key, scan, action, mods)
            if requested_action:
                self.renderer.action_waiting = requested_action
            return
        
        self.renderer.on_potential_shortcut(key, action, mods)