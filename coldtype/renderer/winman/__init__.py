import time, threading, sys

from coldtype.renderer.config import ColdtypeConfig
from coldtype.renderer.winman.passthrough import WinmanPassthrough
from coldtype.renderer.winman.glfwskia import glfw, skia, WinmanGLFWSkia, WinmanGLFWSkiaBackground
from coldtype.renderer.winman.midi import MIDIWatcher, rtmidi
from coldtype.renderer.winman.webview import WinmanWebview
from coldtype.renderer.winman.websocket import WinmanWebsocket
from coldtype.renderer.winman.blender import WinmanBlender
from coldtype.renderable import Action


last_line = ''
new_line_event = threading.Event()

def monitor_stdin():
    # https://stackoverflow.com/questions/27174736/how-to-read-most-recent-line-from-stdin-in-python
    global last_line
    global new_line_event

    def keep_last_line():
        global last_line, new_line_event
        for line in sys.stdin:
            last_line = line
            new_line_event.set()

    keep_last_line_thread = threading.Thread(target=keep_last_line)
    keep_last_line_thread.daemon = True
    keep_last_line_thread.start()


class Winmans():
    def __init__(self, renderer, config:ColdtypeConfig):
        self.renderer = renderer
        self.config = config

        self.pt = WinmanPassthrough()

        self.glsk:WinmanGLFWSkia = None
        self.ws:WinmanWebsocket = None
        self.wv:WinmanWebview = None
        self.midi:MIDIWatcher = None
        self.b3d:WinmanBlender = None

        self.last_time = -1
        self.refresh_delay = self.config.refresh_delay
        self.backoff_refresh_delay = self.refresh_delay

        self.playing = 0
        self.preloaded_frames = []
        self.playing_preloaded_frame = -1

        self.bg = False
        if (config.args.is_subprocess
            or config.args.all
            or config.args.release
            or config.args.build
            ):
            self.bg = True

    def should_glfwskia(self):
        return glfw is not None and skia is not None and not self.config.no_viewer
    
    def should_webviewer(self):
        return self.config.webviewer
    
    def should_midi(self):
        return rtmidi and not self.config.no_midi
    
    def should_blender(self):
        return self.config.blender_watch
    
    def add_viewers(self):
        if not self.bg:
            monitor_stdin()

        if self.config.websocket or self.should_webviewer():
            self.ws = WinmanWebsocket(self.config, self.renderer)

        if self.should_glfwskia():
            self.glsk = WinmanGLFWSkia(self.config, self.renderer)
        
        if self.should_webviewer():
            self.wv = WinmanWebview(self.config, self.renderer)
        
        if self.should_blender():
            self.b3d = WinmanBlender()
        
        if self.should_midi():
            self.midi = MIDIWatcher(self.config,
                self.renderer.state,
                self.renderer.execute_string_as_shortcut_or_action)
        elif self.config.args.midi_info:
            print(">>> pip install rtmidi")

    def did_reload(self, filepath):
        if self.b3d:
            self.b3d.reload(filepath)
    
    def found_blend_files(self, blend_files):
        if len(blend_files) > 0:
            if self.b3d:
                self.b3d.launch(blend_files[0])
    
    def all(self):
        return [self.pt, self.glsk, self.wv, self.b3d]
    
    def map(self):
        for wm in self.all():
            if wm:
                yield wm
    
    def set_title(self, text):
        [wm.set_title(text) for wm in self.map()]
    
    def reset(self):
        [wm.reset() for wm in self.map()]
    
    def terminate(self):
        [wm.terminate() for wm in self.map()]
    
    def toggle_playback(self):
        if self.playing == 0:
            self.playing = 1
        else:
            self.playing = 0
    
    def preload_frames(self, passes):
        for rp in passes:
            self.preloaded_frames.append(rp.output_path)
        self.playing_preloaded_frame = 0
    
    def stop_playing_preloaded(self):
        self.playing_preloaded_frame = -1
    
    def toggle_play_preloaded(self):
        if self.playing_preloaded_frame >= 0:
            self.playing_preloaded_frame = -1
            self.preloaded_frames = []
        else:
            anm = self.renderer.animation()
            passes = anm.passes(Action.RenderAll, self.renderer.state, anm.all_frames())
            self.preload_frames(passes)
    
    def should_close(self):
        return any([wm.should_close() for wm in self.map()])
    
    def send_to_external(self, action, **kwargs):
        if self.ws:
            self.ws.send_to_external(action, **kwargs)
    
    def poll(self):
        if self.glsk:
            self.glsk.poll()
    
    def turn_over(self):
        if self.midi:
            if self.midi.monitor(self.playing):
                self.renderer.action_waiting = Action.PreviewStoryboard

        if self.ws:
            self.ws.read_messages()

        render_previews = len(self.renderer.previews_waiting_to_paint) > 0
        if not render_previews:
            self.backoff_refresh_delay += 0.01
            if self.backoff_refresh_delay >= 0.25:
                self.backoff_refresh_delay = 0.25
            return []
        
        self.backoff_refresh_delay = self.refresh_delay

        did_preview = []
        if self.glsk:
            did_preview.append(self.glsk.turn_over())
        
        if self.wv:
            did_preview.append(self.wv.turn_over())
        
        return did_preview
    
    def run_loop(self):
        while (not self.renderer.dead
            and not self.should_close()
            ):
            t2 = time.time()
            td2 = t2 - self.last_time

            spf = 0.1
            if self.renderer.last_animation:
                spf = 1 / float(self.renderer.last_animation.timeline.fps)

                if td2 >= spf:
                    self.last_time = t2
                else:
                    self.poll()
                    continue
            
            if self.renderer.last_animation and self.playing_preloaded_frame >= 0 and len(self.preloaded_frames) > 0:
                if self.glsk:
                    self.glsk.show_preloaded_frame(self.preloaded_frames[self.playing_preloaded_frame])
                
                self.playing_preloaded_frame += 1
                if self.playing_preloaded_frame == len(self.preloaded_frames):
                    self.playing_preloaded_frame = 0
                
                time.sleep(0.01)
            
            else:
                time.sleep(self.backoff_refresh_delay)
                self.last_time = t2
                
                # TODO the main turn_over, why is it like this?
                self.last_previews = self.renderer.turn_over()

                global last_line
                if last_line:
                    lls = last_line.strip()
                    if lls:
                        self.renderer.on_stdin(lls)
                    last_line = None
            
            self.poll()
    
        self.renderer.on_exit(restart=False)