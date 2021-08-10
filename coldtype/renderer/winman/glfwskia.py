from coldtype.renderer.winman.passthrough import WinmanPassthrough

import time as ptime
from subprocess import Popen, PIPE
from pathlib import Path

from coldtype.color import rgb

try:
    import glfw
except ImportError:
    glfw = None

try:
    import skia
    import coldtype.fx.skia as skfx
except ImportError:
    skia = None
    skfx = None

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
        GL = None


from coldtype.geometry import Point, Rect, Edge
from coldtype.renderable import Action
from coldtype.renderer.config import ConfigOption, ColdtypeConfig
from coldtype.renderer.keyboard import KeyboardShortcut, REPEATABLE_SHORTCUTS, shortcuts_keyed

from coldtype.pens.svgpen import SVGPen


class WinmanGLFWSkiaBackground(WinmanPassthrough):
    def __init__(self, config:ColdtypeConfig, renderer):
        # TODO is the glfw stuff here actually necessary?

        if not glfw.init():
            raise RuntimeError('glfw.init() failed')
        
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        window = glfw.create_window(640, 480, '', None, None)
        glfw.make_context_current(window)

        self.context = skia.GrDirectContext.MakeGL()


class WinmanGLFWSkia():
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

        self.typeface = skia.Typeface.MakeFromFile(str(Path(__file__).parent / "../../demo/RecMono-CasualItalic.ttf"))

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
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(self.window, self.on_mouse_move)
        glfw.set_scroll_callback(self.window, self.on_scroll)
        glfw.set_window_focus_callback(self.window, self.on_focus)

        self.set_window_opacity()

        self.prev_scale = self.get_content_scale()
        self.context = skia.GrDirectContext.MakeGL()
        
        self.copy_previews_to_clipboard = False
    
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
    
    def calculate_window_size(self, previews):
        rects = []
        dscale = self.renderer.state.preview_scale
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
    
    def on_key(self, win, key, scan, action, mods):
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
    
    def turn_over(self):
        frect, rects, dscale, needs_new_context = self.calculate_window_size(self.renderer.previews_waiting_to_paint)

        if needs_new_context:
            self.create_surface(frect)
            self.update_window(frect)

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        did_preview = []

        with self.surface as canvas:
            canvas.clear(skia.Color4f(0.3, 0.3, 0.3, 1))
            if self.config.window_transparent:
                canvas.clear(skia.Color4f(0.3, 0.3, 0.3, 0))
            
            for idx, (render, result, rp) in enumerate(self.renderer.previews_waiting_to_paint):
                rect = rects[idx].offset((frect.w-rects[idx].w)/2, 0).round()

                if self.copy_previews_to_clipboard:
                    try:
                        svg = SVGPen.Composite(result, render.rect, viewBox=render.viewBox)
                        print(svg)
                        process = Popen(
                            'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=PIPE)
                        process.communicate(svg.encode('utf-8'))
                    except:
                        print("failed to copy to clipboard")

                try:
                    self.draw_preview(idx, dscale, canvas, rect, (render, result, rp))
                    did_preview.append(rp)
                except Exception as e:
                    short_error = self.renderer.print_error()
                    paint = skia.Paint(AntiAlias=True, Color=skia.ColorRED)
                    canvas.drawString(short_error, 10, 32, skia.Font(None, 36), paint)
            
            self.copy_previews_to_clipboard = False
        
        self.surface.flushAndSubmit()
        glfw.swap_buffers(self.window)
        return did_preview
    
    def poll(self):
        glfw.poll_events()
    
    def show_preloaded_frame(self, path):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        with self.surface as canvas:
            if not self.config.window_transparent:
                c = self.renderer.last_animation.bg
                canvas.clear(c.skia())
            image = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(path)))
            canvas.drawImage(image, 0, 0)
        
        self.surface.flushAndSubmit()
        glfw.swap_buffers(self.window)

    def draw_preview(self, idx, scale, canvas, rect, waiter):
        if isinstance(waiter[1], Path) or isinstance(waiter[1], str):
            image = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(waiter[1])))
            if image:
                canvas.drawImage(image, rect.x, rect.y)
            return
        
        render, result, rp = waiter
        error_color = rgb(1, 1, 1).skia()
        canvas.save()
        canvas.translate(0, self.window_scrolly)
        canvas.translate(rect.x, rect.y)
        
        if not self.config.window_transparent:
            canvas.drawRect(skia.Rect(0, 0, rect.w, rect.h), skia.Paint(Color=render.bg.skia()))
        
        if not hasattr(render, "show_error"):
            canvas.scale(scale, scale)
        
        if render.clip:
            canvas.clipRect(skia.Rect(0, 0, rect.w, rect.h))
        
        if render.direct_draw:
            try:
                render.run(rp, self.renderer.state, canvas)
            except Exception as e:
                short_error = self.renderer.print_error()
                render.show_error = short_error
                error_color = rgb(0, 0, 0).skia()
        else:
            if render.composites:
                comp = result.ch(skfx.precompose(render.rect))
                if not self.renderer.last_render_cleared:
                    render.last_result = comp
                else:
                    render.last_result = None
            else:
                comp = result
            
            render.draw_preview(1.0, canvas, render.rect, comp, rp)
        
        if hasattr(render, "show_error"):
            paint = skia.Paint(AntiAlias=True, Color=error_color)
            canvas.drawString(render.show_error, 30, 70, skia.Font(self.typeface, 50), paint)
            canvas.drawString("> See process in terminal for traceback", 30, 120, skia.Font(self.typeface, 32), paint)
        
        canvas.restore()

    def terminate(self):
        glfw.terminate()

        if self.context:
            self.context.abandonContext()