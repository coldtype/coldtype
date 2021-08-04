try:
    import glfw
except ImportError:
    glfw = None

try:
    import skia
except ImportError:
    skia = None

# source: https://github.com/PixarAnimationStudios/USD/issues/1372

def monkeypatch_ctypes():
    import os
    import ctypes.util
    uname = os.uname()
    if uname.sysname == "Darwin" and uname.release >= "20.":
        real_find_library = ctypes.util.find_library
        def find_library(name):
            if name in {"OpenGL", "GLUT"}:  # add more names here if necessary
                return f"/System/Library/Frameworks/{name}.framework/{name}"
            return real_find_library(name)
        ctypes.util.find_library = find_library
    return

try:
    from OpenGL import GL
except ImportError:
    monkeypatch_ctypes()
    try:
        from OpenGL import GL
    except:
        print("pip install PyOpenGL")
        GL = None

from coldtype.geometry import Point, Rect, Edge
from coldtype.renderer.state import Keylayer, Action
from coldtype.renderer.config import ConfigOption, ColdtypeConfig
from coldtype.renderer.keyboard import KeyboardShortcut, REPEATABLE_SHORTCUTS, shortcuts_keyed


class WindowManagerPassthrough():
    def __init__(self):
        self.context = None

    def set_title(self, text):
        print("TITLE", text)
    
    def terminate(self):
        pass

    def reset(self):
        pass

    def preview_scale(self):
        return 1


class WindowManagerBackgroundRender(WindowManagerPassthrough):
    def __init__(self, config:ColdtypeConfig, renderer):
        # TODO is the glfw stuff here actually necessary?

        if not glfw.init():
            raise RuntimeError('glfw.init() failed')
        
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        window = glfw.create_window(640, 480, '', None, None)
        glfw.make_context_current(window)

        self.context = skia.GrDirectContext.MakeGL()


class WindowManager():
    def __init__(self, config:ColdtypeConfig, renderer, background=False):
        self.config = config
        self.window = None
        self.background = background
        self.renderer = renderer
        self.primary_monitor = None
        self.last_rect = None
        self.all_shortcuts = shortcuts_keyed()
        self.prev_scale = 0
        self.surface = None

        if not glfw.init():
            raise RuntimeError('glfw.init() failed')
        
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        
        if self.config.window_transparent:
            glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
            glfw.window_hint(glfw.DECORATED, glfw.FALSE)
        else:
            glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.FALSE)
        
        if self.config.window_passthrough:
            try:
                glfw.window_hint(0x0002000D, glfw.TRUE)
                # glfw.window_hint(glfw.MOUSE_PASSTHROUGH, glfw.TRUE)
            except glfw.GLFWError:
                print("failed to hint window for mouse-passthrough")

        if self.config.window_background:
            glfw.window_hint(glfw.FOCUSED, glfw.FALSE)
        
        if self.config.window_float:
            glfw.window_hint(glfw.FLOATING, glfw.TRUE)

        if not self.background:
            self.window = glfw.create_window(int(10), int(10), '', None, None)
        
        self.window_scrolly = 0
        self.window_focus = 0

        self.find_primary_monitor()

        glfw.make_context_current(self.window)

        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_char_callback(self.window, self.on_character)
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(self.window, self.on_mouse_move)
        glfw.set_scroll_callback(self.window, self.on_scroll)
        glfw.set_window_focus_callback(self.window, self.on_focus)

        self.set_window_opacity()
        self.prev_scale = self.get_content_scale()

        self.context = skia.GrDirectContext.MakeGL()
    
    def find_primary_monitor(self):
        self.primary_monitor = glfw.get_primary_monitor()
        found_primary = None
        if self.config.monitor_name:
            remn = self.config.monitor_name
            monitors = glfw.get_monitors()
            matches = []
            if remn == "list":
                print("> MONITORS")
            for monitor in monitors:
                mn = glfw.get_monitor_name(monitor)
                if remn == "list":
                    print("    -", mn.decode("utf-8"))
                elif remn in str(mn):
                    matches.append(monitor)
            if len(matches) > 0:
                found_primary = matches[0]
            if found_primary:
                self.primary_monitor = found_primary
    
    def create_surface(self, rect):
        backend_render_target = skia.GrBackendRenderTarget(
            int(rect.w), int(rect.h), 0, 0,
            skia.GrGLFramebufferInfo(0, GL.GL_RGBA8))
        
        self.surface = skia.Surface.MakeFromBackendRenderTarget(
            self.context,
            backend_render_target,
            skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType,
            skia.ColorSpace.MakeSRGB())
        
        assert self.surface is not None

    def get_content_scale(self):
        u_scale = self.config.window_content_scale
        
        if u_scale:
            return u_scale
        elif glfw and not self.renderer.args.no_viewer:
            if self.primary_monitor:
                return glfw.get_monitor_content_scale(self.primary_monitor)[0]
            else:
                return glfw.get_window_content_scale(self.window)[0]
        else:
            return 1
    
    def content_scale_changed(self):
        scale_x = self.get_content_scale()
        if scale_x != self.prev_scale:
            self.prev_scale = scale_x
            return True
        return False
    
    def preview_scale(self):
        return self.renderer.state.preview_scale
    
    def calculate_window_size(self, previews):
        rects = []
        dscale = self.preview_scale()
        w = 0
        llh = -1
        lh = -1
        h = 0
        for render, result, rp in previews:
            if hasattr(render, "show_error"):
                sr = render.rect
            else:
                sr = render.rect.scale(dscale, "mnx", "mny").round()
            w = max(sr.w, w)
            if render.layer:
                rects.append(Rect(0, llh, sr.w, sr.h))
            else:
                rects.append(Rect(0, lh+1, sr.w, sr.h))
                llh = lh+1
                lh += sr.h + 1
                h += sr.h + 1
        h -= 1

        frect = Rect(0, 0, w, h)

        if not self.last_rect:
            needs_new_context = True
        else:
            needs_new_context = self.last_rect != frect
        
        self.last_rect = frect
        return frect, rects, dscale, needs_new_context
    
    def update_window(self, frect):
        m_scale = self.get_content_scale()
        scale_x, scale_y = m_scale, m_scale

        ww = int(frect.w/scale_x)
        wh = int(frect.h/scale_y)
        glfw.set_window_size(self.window, ww, wh)

        pin = self.config.window_pin

        if pin:
            work_rect = Rect(glfw.get_monitor_workarea(self.primary_monitor))
            wrz = work_rect.zero()
            edges = Edge.PairFromCompass(pin)
            pinned = wrz.take(ww, edges[0]).take(wh, edges[1]).round()
            if edges[1] == "mdy":
                pinned = pinned.offset(0, -30)
            pinned = pinned.flip(wrz.h)
            pinned = pinned.offset(*work_rect.origin())
            wpi = self.config.window_pin_inset
            pinned = pinned.inset(-wpi[0], wpi[1])
            glfw.set_window_pos(self.window, pinned.x, pinned.y)
        else:
            glfw.set_window_pos(self.window, 0, 0)
    
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
    
    def should_close(self):
        return glfw.window_should_close(self.window)
    
    def focus(self, force=False):
        if self.window_focus == 0 or force:
            glfw.focus_window(self.window)
            return True
        return False
    
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
        pos[1] = self.last_rect.h - pos[1]
        requested_action = self.renderer.state.on_mouse_button(pos, btn, action, mods)
        if requested_action:
            self.renderer.action_waiting = requested_action
    
    def on_mouse_move(self, _, xpos, ypos):
        if not self.allow_mouse():
            return
        
        pos = Point((xpos, ypos)).scale(2)
        pos[1] = self.last_rect.h - pos[1]
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
        
        self.on_potential_shortcut(key, action, mods)
    
    def repeatable_shortcuts(self):
        return REPEATABLE_SHORTCUTS
    
    def on_potential_shortcut(self, key, action, mods):
        for shortcut, options in self.all_shortcuts.items():
            for modifiers, skey in options:
                if key != skey:
                    continue

                if isinstance(mods, list):
                    mod_matches = mods
                else:
                    mod_matches = [0, 0, 0, 0]
                    for idx, mod in enumerate([glfw.MOD_SUPER, glfw.MOD_ALT, glfw.MOD_SHIFT, glfw.MOD_CONTROL]):
                        if mod in modifiers:
                            if mods & mod:
                                mod_matches[idx] = 1
                        elif mod not in modifiers:
                            if not (mods & mod):
                                mod_matches[idx] = 1
                
                mod_match = all(mod_matches)
                
                if not mod_match and len(modifiers) == 0 and isinstance(mods, list):
                    mod_match = True
                
                if len(modifiers) == 0 and mods != 0 and not isinstance(mods, list):
                    mod_match = False
                
                if mod_match and key == skey:
                    if (action == glfw.REPEAT and shortcut in self.repeatable_shortcuts()) or action == glfw.PRESS:
                        #print(shortcut, modifiers, skey, mod_match)
                        return self.renderer.on_shortcut(shortcut)
    
    def terminate(self):
        glfw.terminate()

        if self.context:
            self.context.abandonContext()