from coldtype.pens.datimage import DATImage
import tempfile, traceback, threading, multiprocessing
import argparse, importlib, inspect, json, math
import sys, os, re, signal, tracemalloc, shutil
import platform, pickle, string, datetime
import numpy as np

import time as ptime
from pathlib import Path
from typing import Tuple
from pprint import pprint
from random import random
from runpy import run_path
from subprocess import call, Popen, PIPE, STDOUT
from random import shuffle, Random
from more_itertools import distribute
from docutils.core import publish_doctree
from functools import partial, partialmethod

from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import TCPServer

import coldtype
from coldtype.helpers import *
from drafting.geometry import Rect, Point, Edge
from drafting.text.reader import Font as DraftingFont

from coldtype.renderer.watchdog import AsyncWatchdog
from coldtype.renderer.state import RendererState, Keylayer, Overlay
from coldtype.renderable import renderable, Action, animation
from coldtype.pens.datpen import DATPen, DATPens

from drafting.pens.svgpen import SVGPen
from drafting.pens.jsonpen import JSONPen

from coldtype.renderer.keyboard import KeyboardShortcut, SHORTCUTS, REPEATABLE_SHORTCUTS, symbol_to_glfw

try:
    import skia
    from coldtype.pens.skiapen import SkiaPen
except ImportError:
    skia = None
    SkiaPen = None

try:
    import drawBot as db
except ImportError:
    db = None

try:
    import glfw
    from OpenGL import GL
except ImportError:
    glfw = None
    GL = None

from coldtype.renderer.utils import *

_random = Random()

from time import sleep

try:
    import rtmidi
except ImportError:
    pass

try:
    import pyaudio, wave, soundfile
except ImportError:
    pyaudio = None
    wave = None

try:
    import psutil
    process = psutil.Process(os.getpid())
except ImportError:
    process = None

DARWIN = platform.system() == "Darwin"

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

def show_tail(p):
    for line in p.stdout:
        print(line.decode("utf-8").split(">>")[-1].strip().strip("\n"))

WEBSOCKET_PORT = None

class WebViewerHandler(SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(
            (Path(__file__).parent.parent / "webserver/webviewer.html")
                .read_text()
                .replace("localhost:8007", f"localhost:{WEBSOCKET_PORT}")
                .encode("utf8"))

    def do_HEAD(self):
        self._set_headers()
    
    def log_message(self, format, *args):
        pass

class DataSourceThread(threading.Thread):
    def __init__(self, filepath):
        self.filepath = filepath
        self.program = run_path(self.filepath)
        self.should_run = True
        threading.Thread.__init__(self)
    
    def run(self):
        print("Running data thread for:", self.filepath.relative_to(Path.cwd()))
        while self.should_run:
            self.program["run"]()
            self.interval = self.program.get("INTERVAL", 0.5)
            ptime.sleep(self.interval)

class Renderer():
    def Argparser(name="coldtype", file=True, defaults={}, nargs=[]):
        parser = argparse.ArgumentParser(prog=name, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        
        if file:
            parser.add_argument("file", type=str, nargs="?", help="The source file for a coldtype render")
        for narg in nargs:
            parser.add_argument(narg[0], nargs="?", default=narg[1])
        
        pargs = dict(
            version=parser.add_argument("-v", "--version", action="store_true", default=False, help="Display version"),

            no_watch=parser.add_argument("-nw", "--no-watch", action="store_true", default=False, help="Preventing watching for changes to source files"),

            no_viewer=parser.add_argument("-nv", "--no-viewer", action="store_true", default=False, help="Prevent showing skia/glfw viewer"),

            websocket=parser.add_argument("-ws", "--websocket", action="store_true", default=False, help="Should the server run a web socket?"),

            webviewer=parser.add_argument("-wv", "--webviewer", action="store_true", default=False, help="Do you want to live-preview in a webviewer instead of with a glfw-skia window?"),

            webviewer_port=parser.add_argument("-wvp", "--webviewer-port", type=int, default=8008, help="What port should the webviewer run on? (provided -wv is passed)"),

            port=parser.add_argument("-p", "--port", type=int, default=8007, help="What port should the websocket run on (provided -ws is passed)"),
        
            websocket_external=parser.add_argument("-wse", "--websocket-external", type=str, default=None, help="What address should a websocket connection be made to, for control of external coldtype program?"),

            no_midi=parser.add_argument("-nm", "--no-midi", action="store_true", default=False, help="Midi is on by default, do you want to turn it off?"),
            
            save_renders=parser.add_argument("-sv", "--save-renders", action="store_true", default=False, help="Should the renderer create image artifacts?"),
            
            rasterizer=parser.add_argument("-r", "--rasterizer", type=str, default=None, choices=["drawbot", "cairo", "svg", "skia", "pickle"], help="Which rasterization engine should coldtype use to create artifacts?"),

            cpu_render=parser.add_argument("-cpu", "--cpu-render", action="store_true", default=False, help="Should final rasters be performed without a GPU context?"),
            
            scale=parser.add_argument("-s", "--scale", type=float, default=1.0, help="When save-renders is engaged, what scale should images be rasterized at? (Useful for up-rezing)"),

            preview_scale=parser.add_argument("-ps", "--preview-scale", type=float, default=1.0, help="What size should previews be shown at?"),

            #preview_audio=parser.add_argument("-pa", "--preview-audio", action="store_true", default=False, help="Should the renderer attempt to playback audio?"),
            
            all=parser.add_argument("-a", "--all", action="store_true", default=False, help="If rendering an animation, pass the -a flag to render all frames sequentially"),

            multiplex=parser.add_argument("-mp", "--multiplex", action="store_true", default=False, help="Render in multiple processes"),

            composite=parser.add_argument("-c", "--composite", action="store_true", default=False, help="Should the next render composite onto the previous render?"),

            memory=parser.add_argument("-mm", "--memory", action="store_true", default=False, help="Show statistics about memory usage?"),

            midi_info=parser.add_argument("-mi", "--midi-info", action="store_true", default=False, help="Show available MIDI devices"),

            show_time=parser.add_argument("-st", "--show-time", action="store_true", default=False, help="Show time for each render"),

            is_subprocess=parser.add_argument("-isp", "--is-subprocess", action="store_true", default=False, help=argparse.SUPPRESS),

            thread_count=parser.add_argument("-tc", "--thread-count", type=int, default=defaults.get("thread_count", 8), help="How many threads when multiplexing?"),

            no_sound=parser.add_argument("-ns", "--no-sound", action="store_true", default=False, help="Don’t make sound"),

            window_opacity=parser.add_argument("-wo", "--window-opacity", type=float, help="opacity of the window, from >0 to 1 (defaults to 1 unless overridden in .coldtype.py file)"),

            monitor_name=parser.add_argument("-mn", "--monitor-name", type=str, help="the name of the monitor to open the window in; pass 'list' to list all monitor names"),

            window_pin=parser.add_argument("-wp", "--window-pin", type=str, help="where to pin the window, if you want to pin the window"),

            window_pin_inset=parser.add_argument("-wpi", "--window-pin-inset", type=str, help="how much to 'inset' the pin of the window"),

            window_content_scale=parser.add_argument("-wcs", "--window-content-scale", type=float, default=None, help="do you want to override the reported content-scale?"),

            window_float=parser.add_argument("-wf", "--window-float", action="store_true", default=False, help="should the window float on top of everything?"),

            window_transparent=parser.add_argument("-wt", "--window-transparent", action="store_true", default=False, help="should the window background be transparent?"),

            window_passthrough=parser.add_argument("-wpass", "--window-passthrough", action="store_true", default=False, help="should the window ignore all mouse interaction?"),
            
            format=parser.add_argument("-fmt", "--format", type=str, default=None, help="What image format should be saved to disk?"),

            indices=parser.add_argument("-i", "--indices", type=str, default=None),

            output_folder=parser.add_argument("-of", "--output-folder", type=str, default=None, help="If you don’t want to render to the default output location, specify that here."),

            monitor_lines=parser.add_argument("-ml", "--monitor-lines", action="store_true", default=False, help=argparse.SUPPRESS),

            filter_functions=parser.add_argument("-ff", "--filter-functions", type=str, default=None, help="Names of functions to render"),

            sidecar=parser.add_argument("-sc", "--sidecar", type=str, default=None, help="A file to run alongside your coldtype source file (like a file that processes data or keystrokes), that will run in a managed thread"),

            tails=parser.add_argument("-tl", "--tails", type=str, default=None, help="File to tail, comma-separated (no whitespace); results will print output to the normal process output"),

            hide_keybuffer=parser.add_argument("-hkb", "--hide-keybuffer", action="store_true", default=False, help="Should the keybuffer be shown?"),

            show_exit_code=parser.add_argument("-sec", "--show-exit-code", action="store_true", default=False, help=argparse.SUPPRESS),

            show_render_count=parser.add_argument("-src", "--show-render-count", action="store_true", default=False, help=argparse.SUPPRESS),

            frame_offsets=parser.add_argument("-fo", "--frame-offsets", type=str, default=None, help=argparse.SUPPRESS),

            disable_syntax_mods=parser.add_argument("-dsm", "--disable-syntax-mods", action="store_true", default=False, help="Coldtype has some optional syntax modifications that require copying the source to a new tempfile before running — would you like to skip this to preserve __file__ in your sources?")),
        return pargs, parser
    
    def read_configs(self):
        proj = Path(".coldtype.py")
        user = Path("~/.coldtype.py").expanduser()
        self.midi_mapping = {}
        self.hotkey_mapping = {}
        self.py_config = {}
        self.many_increment = 10

        for p in [user, proj]:
            if p.exists():
                try:
                    self.py_config = {
                        **self.py_config,
                        **run_path(str(p), init_globals={
                            "__MIDI__": self.midi_mapping,
                            "__HOTKEYS__": self.hotkey_mapping,
                        })
                    }
                    self.midi_mapping = self.py_config.get("MIDI", self.midi_mapping)
                    self.hotkey_mapping = self.py_config.get("HOTKEYS", self.hotkey_mapping)
                    self.many_increment = self.py_config.get("MANY_INCREMENT", self.many_increment)
                except Exception as e:
                    print("Failed to load config", p)
                    print("Exception:", e)

    def __init__(self, parser, no_socket_ok=False):
        sys.path.insert(0, os.getcwd())

        self.read_configs()

        self.parser = parser
        self.args = parser.parse_args()
        if self.args.is_subprocess or self.args.all:
            self.args.no_watch = True
        
        self.disable_syntax_mods = self.args.disable_syntax_mods
        self.filepath = None
        self.state = RendererState(self)

        self.observers = []
        self.watchees = []
        self.sidecar_threads = []
        self.tails = []
        self.watchee_mods = {}
        
        self.rasterizer_warning = None
        
        if not self.reset_filepath(self.args.file if hasattr(self.args, "file") else None):
            self.dead = True
            return
        else:
            self.dead = False
        
        self.state.preview_scale = self.args.preview_scale
        
        monitor_stdin()
        
        if self.args.version:
            print(">>>", coldtype.__version__)
            self.dead = True
            return

        self.program = None
        self.exit_code = 0

        self.line_number = -1
        self.last_renders = []

        # for multiplex mode
        self.running_renderers = []
        self.completed_renderers = []

        self.action_waiting = None
        self.requests_waiting = []
        self.waiting_to_render = []
        self.previews_waiting_to_paint = []
        self.preloaded_frames = []
        self.playing_preloaded_frame = -1
        self.glfw_last_time = -1
        self.last_animation = None
        self.last_rect = None
        self.playing = 0
        self.hotkeys = None
        self.context = None
        self.surface = None
        self.transparent = False

        if self.args.filter_functions:
            self.function_filters = [f.strip() for f in self.args.filter_functions.split(",")]
        else:
            self.function_filters = []
        self.multiplexing = self.args.multiplex
        self._should_reload = False

        self.recurring_actions = {}
    
    def reset_filepath(self, filepath):
        self.line_number = -1
        self.stop_watching_file_changes()
        self.state.input_history.clear()
        self.state._frame_offsets = {}
        self.state._initial_frame_offsets = {}

        if filepath:
            self.filepath = Path(filepath).expanduser().resolve()
            if self.filepath.suffix == ".py":
                if not self.filepath.exists(): # write some default code there after a prompt
                    print(">>> That python file does not exist...")
                    create = input(">>> Do you want to create it and add some coldtype boilerplate? (y/n): ")
                    if create.lower() == "y":
                        self.filepath.parent.mkdir(exist_ok=True, parents=True)
                        self.filepath.write_text("from coldtype import *\n\n@renderable()\ndef stub(r):\n    return (DATPen()\n        .oval(r.inset(50))\n        .f(0.8))\n")
                        editor_cmd = self.py_config.get("EDITOR_COMMAND")
                        if editor_cmd:
                            os.system(editor_cmd + " " + str(self.filepath.relative_to(Path.cwd())))
            elif self.filepath.suffix == ".rst":
                if not self.filepath.exists():
                    print(">>> That rst file does not exist")
                    return False
            else:
                print(">>> Coldtype can only read .py and .rst files")
                return False
            self.codepath = None
            self._codepath_offset = 0
            self.watchees = [[Watchable.Source, self.filepath, None]]
            if not self.args.is_subprocess:
                self.watch_file_changes()
                for line in self.filepath.read_text().splitlines():
                    if line.startswith("#coldtype"):
                        print("> Overriding command-line args with:\n    >", line)
                        self.args = self.parser.parse_args(line.replace("#coldtype", "").strip().split(" "))
        else:
            self.watchees = []
            self.filepath = None
            self.codepath = None
        return True

    def watchee_paths(self):
        return [w[1] for w in self.watchees]
    
    def renderable_error(self):
        stack = traceback.format_exc()
        print(stack)
        r = Rect(1200, 300)
        render = renderable(r)
        res = DATPens([
            DATPen().rect(r).f(coldtype.Gradient.V(r,
            coldtype.hsl(_random.random(), l=0.3),
            coldtype.hsl(_random.random(), l=0.3))),
        ])
        render.show_error = stack.split("\n")[-2]
        return render, res

    def show_error(self):
        if self.playing > 0:
            self.playing = -1
        print("============================")
        print(">>> Error in source file <<<")
        print("============================")
        render, res = self.renderable_error()
        self.previews_waiting_to_paint.append([render, res, None])
    
    def show_message(self, message, scale=1):
        print(message)
    
    def apply_syntax_mods(self, source_code):
        if self.disable_syntax_mods:
            return source_code
        
        self._codepath_offset = 0
        
        def inline_other(x):
            #cwd = self.filepath.relative_to(Path.cwd())
            cwd = Path.cwd()
            #print(">>>>>>>>>>>>>>>>>>>>>>>", cwd)
            path = Path(cwd / (x.group(1).replace(".", "/")+".py"))
            if path not in self.watchee_paths():
                self.watchees.append([Watchable.Source, path, None])
            src = path.read_text()
            self._codepath_offset = len(src.split("\n"))
            return src

        source_code = re.sub(r"from ([^\s]+) import \* \#INLINE", inline_other, source_code)
        source_code = re.sub(r"\-\.[A-Za-z_ƒ]+([A-Za-z_0-9]+)?\(", ".nerp(", source_code)
        source_code = re.sub(r"([\s]+)Ƨ\(", r"\1nerp(", source_code)
        source_code = re.sub(r"λ\s?([/\.\@]{1,2})", r"lambda xxx: xxx\1", source_code)
        #source_code = re.sub(r"λ\.", "lambda x: x.", source_code)
        source_code = re.sub(r"λ", "lambda ", source_code)
        #source_code = re.sub(r"ßDPS\(([^\)]+)\)", r"(ß:=DPS(\1))", source_code)

        while "nerp(" in source_code:
            start = source_code.find("nerp(")
            end = -1
            i = 5
            depth = 1
            c = source_code[start+i]
            while depth > 0 and c:
                #print(c, depth)
                if c == "(":
                    depth += 1
                elif c== ")":
                    depth -= 1
                i += 1
                c = source_code[start+i]
            end = start+i
            source_code = source_code[:start] + "noop()" + source_code[end:]
            #print(start, end)
        
        return source_code

    def reload(self, trigger):
        if skia and SkiaPen:
            DATPen._pen_class = SkiaPen
            DATPen._context = self.context

        if not self.filepath:
            self.program = dict(no_filepath=True)
            pass # ?
        else:
            if self.filepath.suffix == ".rst":
                doctree = publish_doctree(self.filepath.read_text())
                def is_code_block(node):
                    if node.tagname == "literal_block":
                        classes = node.attributes["classes"]
                        # ok the "ruby" here is an ugly hack but it's so I can hide certain code
                        # from a printed rst
                        if "code" in classes and ("python" in classes or "ruby" in classes):
                            return True
                    return False
                code_blocks = doctree.traverse(condition=is_code_block)
                source_code = [block.astext() for block in code_blocks]
                if self.codepath:
                    self.codepath.unlink()
                with tempfile.NamedTemporaryFile("w", prefix="coldtype_rst_src", suffix=".py", delete=False) as tf:
                    tf.write("\n".join(source_code))
                    self.codepath = Path(tf.name)
            
            elif self.filepath.suffix == ".py":
                if self.disable_syntax_mods:
                    self.codepath = self.filepath
                else:
                    source_code = self.apply_syntax_mods(self.filepath.read_text())
                    if self.codepath:
                        self.codepath.unlink()
                    with tempfile.NamedTemporaryFile("w", prefix="coldtype_py_mod", suffix=".py", delete=False) as tf:
                        tf.write(source_code)
                        self.codepath = Path(tf.name)
            else:
                raise Exception("No code found in file!")
            
            try:
                self.state.reset()
                self.program = run_path(str(self.codepath), init_globals={
                    "__COLDTYPE__": True,
                    "__CONTEXT__": self.context,
                    "__FILE__": self.filepath,
                    "__sibling__": partial(sibling, self.filepath)
                })

                full_restart = False

                for r in self.renderables(Action.PreviewStoryboardReload):
                    if isinstance(r, animation):
                        if r.name not in self.state._frame_offsets:
                            full_restart = True
                            for i, s in enumerate(r.storyboard):
                                self.state.add_frame_offset(r.name, s)
                        else:
                            lasts = self.state._initial_frame_offsets[r.name]
                            if str(lasts) != str(r.storyboard):
                                del self.state._frame_offsets[r.name]
                                del self.state._initial_frame_offsets[r.name]
                                for s in r.storyboard:
                                    self.state.add_frame_offset(r.name, s)
                        
                        self.last_animation = r
                        if pyaudio and not self.args.is_subprocess and r.audio:
                            self.paudio_source = soundfile.SoundFile(r.audio, "r+")
                            #self.paudio_source = wave.open(str(r.audio), "rb")
                            self.paudio_preview = 0
                        
                        if not r.audio:
                            self.paudio_source = None
                
                if full_restart:
                    fos = {}
                    if self.args.frame_offsets:
                        fos = eval(self.args.frame_offsets)
                        for k, v in fos.items():
                            self.state.adjust_keyed_frame_offsets(k, lambda i, o: v[i])
                    
                if self.program.get("COLDTYPE_NO_WATCH"):
                    return True
            except SystemExit:
                self.on_exit(restart=False)
                return True
            except Exception as e:
                self.program = None
                self.show_error()
    
    def animation(self):
        renderables = self.renderables(Action.PreviewStoryboard)
        for r in renderables:
            if isinstance(r, animation):
                return r
    
    def release_fn(self):
        candidate = None
        for k, v in self.program.items():
            if k == "release":
                candidate = v
        return candidate
    
    def normalize_fmt(self, render):
        if self.args.format:
            render.fmt = self.args.format
        if self.args.rasterizer:
            render.rasterizer = self.args.rasterizer

        if render.rasterizer == "skia" and render.fmt in ["png", "pdf"] and skia is None:
            if not self.rasterizer_warning:
                self.rasterizer_warning = True
                print(f"RENDERER> SVG (skia-python not installed)")
            render.rasterizer = "svg"
            render.fmt = "svg"
        elif render.rasterizer == "drawbot" and render.fmt in ["png", "pdf"] and db is None:
            if not self.rasterizer_warning:
                self.rasterizer_warning = True
                print(f"RENDERER> SVG (no drawbot)")
            render.rasterizer = "svg"
            render.fmt = "svg"
    
    def renderables(self, trigger):
        _rs = []
        for k, v in self.program.items():
            if isinstance(v, renderable) and not v.hidden:
                if v not in _rs:
                    self.normalize_fmt(v)
                    _rs.append(v)
        
        for r in _rs:
            output_folder = self.render_to_output_folder(r)
            r.output_folder = output_folder

        if any([r.solo for r in _rs]):
            _rs = [r for r in _rs if r.solo]
            
        if self.function_filters:
            function_patterns = self.function_filters
            print(">>>", function_patterns)
            matches = []
            for r in _rs:
                for fp in function_patterns:
                    try:
                        if re.match(fp, r.name) and r not in matches:
                            matches.append(r)
                    except re.error as e:
                        print("ff regex compilation error", e)
            if len(matches) > 0:
                _rs = matches
            else:
                print(">>> no matches for ff")
        
        if self.args.monitor_lines and trigger != Action.RenderAll:
            func_name = file_and_line_to_def(self.codepath, self.line_number)
            matches = [r for r in _rs if r.name == func_name]
            print(">", matches)
            if len(matches) > 0:
                return matches

        if len(_rs) == 0:
            r = renderable((500, 500))
            def draw(r):
                #ct = coldtype.StyledString("CT", coldtype.Style("assets/ColdtypeObviously-VF.ttf", 500, wdth=0)).pen().round(1)
                #print(ct.value)
                ct = DATPen().vl([('moveTo', [(70.0, 236.0)]), ('qCurveTo', [(76.5, 236.0), (83.0, 237.5), (86.0, 238.0)]), ('qCurveTo', [(80.5, 214.0), (66.0, 153.5), (50.0, 89.0), (35.5, 28.0), (30.0, 3.5)]), ('qCurveTo', [(27.5, 2.5), (20.5, -0.5), (13.0, -2.0), (8.5, -2.0)]), ('qCurveTo', [(-2.0, -2.0), (-15.5, 6.0), (-20.0, 29.5), (-14.5, 74.5), (1.5, 148.5), (15.5, 203.5)]), ('qCurveTo', [(29.5, 259.0), (49.5, 328.0), (67.0, 364.0), (85.5, 377.0), (97.5, 377.0)]), ('qCurveTo', [(106.0, 377.0), (118.0, 374.5), (121.5, 372.0)]), ('qCurveTo', [(116.0, 352.0), (108.0, 323.0), (101.5, 297.5), (94.0, 268.5), (88.5, 247.5)]), ('qCurveTo', [(85.0, 248.5), (75.5, 250.0), (70.5, 250.0)]), ('qCurveTo', [(66.5, 250.0), (60.5, 247.5), (59.5, 244.0)]), ('qCurveTo', [(59.0, 240.0), (64.5, 236.0), (70.0, 236.0)]), ('closePath', []), ('moveTo', [(119.5, 289.5)]), ('lineTo', [(168.0, 289.5)]), ('qCurveTo', [(156.5, 242.5), (133.0, 148.5), (113.5, 67.5), (99.0, 10.5), (96.5, 0.0)]), ('qCurveTo', [(91.5, 0.5), (77.0, 1.0), (71.5, 1.0)]), ('qCurveTo', [(65.5, 1.0), (51.5, 0.5), (46.0, 0.0)]), ('qCurveTo', [(49.0, 10.5), (64.0, 67.5), (84.5, 148.5), (108.0, 242.5), (119.5, 289.5)]), ('closePath', []), ('moveTo', [(127.5, 375.0)]), ('lineTo', [(202.0, 375.0)]), ('qCurveTo', [(200.0, 365.5), (193.0, 337.5), (189.0, 323.5)]), ('qCurveTo', [(186.0, 310.5), (178.5, 281.0), (176.0, 270.0)]), ('qCurveTo', [(166.0, 270.0), (147.0, 270.5), (139.0, 270.5)]), ('qCurveTo', [(131.5, 270.5), (112.0, 270.0), (101.5, 270.0)]), ('qCurveTo', [(104.5, 281.0), (112.0, 310.5), (115.0, 323.5)]), ('qCurveTo', [(119.0, 337.5), (125.5, 365.5), (127.5, 375.0)]), ('closePath', [])])
                return DATPens([
                    DATPen().rect(r).f(coldtype.Gradient.Vertical(r,
                    coldtype.hsl(_random.random()),
                    coldtype.hsl(_random.random()))),
                    ct.align(r.inset(20), "mnx", "mxy").f(1, 0.25)
                    ])
            r.__call__(draw)
            r.blank_renderable = True
            print(">>> No renderables found <<<")
            _rs.append(r)

        return _rs
    
    def render_to_output_folder(self, render):
        if self.args.output_folder:
            return Path(self.args.output_folder).expanduser().resolve()
        elif render.dst:
            return render.dst / (render.custom_folder or render.folder(self.filepath))
        else:
            return (self.filepath.parent if self.filepath else Path(os.getcwd())) / "renders" / (render.custom_folder or render.folder(self.filepath))
    
    def add_paths_to_passes(self, trigger, render, indices):
        output_folder = self.render_to_output_folder(render)
        
        if render.prefix is None:
            if self.filepath is not None:
                prefix = f"{self.filepath.stem}_"
            else:
                prefix = None
        else:
            prefix = render.prefix

        fmt = render.fmt
        rps = []
        for rp in render.passes(trigger, self.state, indices):
            output_path = output_folder / f"{prefix}{rp.suffix}.{fmt}"
            rp.output_path = output_path
            rp.action = trigger
            rps.append(rp)
        
        return output_folder, prefix, fmt, rps

    
    def _single_thread_render(self, trigger, indices=[]) -> Tuple[int, int]:
        if not self.args.is_subprocess:
            start = ptime.time()
        
        if len(self.previews_waiting_to_paint) > 0:
            return 0, 0, []

        prev_renders = self.last_renders
        renders = self.renderables(trigger)
        self.last_renders = renders
        preview_count = 0
        render_count = 0
        output_folder = None
        try:
            for render in renders:
                render.codepath = self.codepath
                render.filepath = self.filepath

                for watch, flag in render.watch:
                    if isinstance(watch, DraftingFont) and not watch.cacheable:
                        if watch.path not in self.watchee_paths():
                            self.watchees.append([Watchable.Font, watch.path, flag])
                        for ext in watch.font.getExternalFiles():
                            if ext not in self.watchee_paths():
                                self.watchees.append([Watchable.Font, ext, flag])
                    elif watch not in self.watchee_paths():
                        self.watchees.append([Watchable.Generic, watch, flag])
                
                did_render = False
                output_folder, prefix, fmt, passes = self.add_paths_to_passes(trigger, render, indices)
                render.last_passes = passes

                #if trigger == Action.RenderAll:
                #    shutil.rmtree(output_folder, ignore_errors=True)

                previewing = (trigger in [
                    Action.Initial,
                    Action.Resave,
                    Action.PreviewStoryboard,
                    Action.PreviewIndices,
                    Action.PreviewStoryboardReload,
                ])
                
                rendering = (self.args.save_renders or trigger in [
                    Action.RenderAll,
                    Action.RenderWorkarea,
                    Action.RenderIndices,
                ])

                self.state.previewing = previewing # TODO too janky?
                self.state.preview_scale = self.preview_scale()
                
                for rp in passes:
                    output_path = rp.output_path

                    try:
                        if render.direct_draw:
                            result = None
                        else:
                            # repopulate last_result across a save
                            if not render.last_result:
                                if len(prev_renders) > 0:
                                    for pr in prev_renders:
                                        if pr.name == render.name and pr.last_result:
                                            render.last_result = pr.last_result
                            result = render.normalize_result(render.run(rp, self.state))
                            if self.args.composite and not render.composites:
                                result = DATPens([render.last_result, result])
                        
                        if self.state.request:
                            self.requests_waiting.append([render, str(self.state.request), None])
                            self.state.request = None
                        
                        if self.state.callback:
                            self.requests_waiting.append([render, self.state.callback, "callback"])
                            self.state.callback = None

                        if not result and not render.direct_draw:
                            #print(">>> No result")
                            result = DATPen().rect(render.rect).f(None)

                        if previewing:
                            if render.direct_draw:
                                self.previews_waiting_to_paint.append([render, None, rp])
                            else:
                                preview_result = render.normalize_result(render.runpost(result, rp, self.state))
                                preview_count += 1
                                if preview_result:
                                    self.previews_waiting_to_paint.append([render, preview_result, rp])
                        
                        if rendering:
                            did_render = True
                            if False:
                                pass
                            else:
                                if render.preview_only:
                                    continue
                                render_count += 1
                                output_path.parent.mkdir(exist_ok=True, parents=True)
                                if render.self_rasterizing:
                                    print(">>> self-rasterized...", output_path.relative_to(Path.cwd()))
                                else:
                                    if render.direct_draw:
                                        self.rasterize(partial(render.run, rp, self.state), render, output_path)
                                    else:
                                        self.rasterize(result or DATPen(), render, output_path)
                                    # TODO a progress bar?
                                    print(">>> saved...", str(output_path.relative_to(Path.cwd())))
                    except:
                        self.show_error()
        except:
            self.show_error()
        if render_count > 0:
            self.show_message(f"Rendered {render_count}")
        
        if not self.args.is_subprocess and self.args.show_time:
            print("TIME >>>", ptime.time() - start)
        
        return preview_count, render_count, renders

    def render(self, trigger, indices=[]) -> Tuple[int, int]:
        if self.args.is_subprocess: # is a child process of a multiplexed render
            if trigger != Action.RenderIndices:
                raise Exception("Invalid child process render action", trigger)
                return 0, 0
            else:
                p, r, _ = self._single_thread_render(trigger, indices=indices)
                if not self.args.no_sound:
                    os.system("afplay /System/Library/Sounds/Pop.aiff")
                self.exit_code = 5 # mark as child-process
                return p, r
        
        elif self.multiplexing and self.animation():
            if trigger in [Action.RenderAll, Action.RenderWorkarea]:
                all_frames = self.animation().all_frames()
                if trigger == Action.RenderAll:
                    frames = all_frames
                elif trigger == Action.RenderWorkarea:
                    timeline = self.animation().timeline
                    try:
                        frames = list(timeline.workareas[0])
                    except:
                        frames = all_frames
                    if len(frames) == 0:
                        frames = all_frames
                self.render_multiplexed(frames)
                trigger = Action.RenderIndices
                indices = [0, all_frames[-1]] # always render first & last from main, to trigger a filesystem-change detection in premiere

        elif self.animation() and trigger == Action.RenderWorkarea:
            all_frames = self.animation().all_frames()
            self._single_thread_render(Action.RenderIndices, [0, all_frames[-1]])
        
        preview_count, render_count, renders = self._single_thread_render(trigger, indices)
        
        if not self.args.is_subprocess and render_count > 0:
            for render in renders:
                result = render.package(self.filepath, self.render_to_output_folder(render))
                if result:
                    self.previews_waiting_to_paint.append([render, result, None])
                else:
                    self.action_waiting = Action.PreviewStoryboard

            self.send_to_external(None, rendered=True)

        return preview_count, render_count
    
    def render_multiplexed(self, frames):
        start = ptime.time()

        print("TC", self.args.thread_count)
        
        group = math.floor(len(frames) / self.args.thread_count)
        ordered_frames = list(frames) #list(range(frames[0], frames[0]+len(frames)))
        shuffle(ordered_frames)
        #subslices = list(chunks(ordered_frames, group))
        subslices = [list(s) for s in distribute(self.args.thread_count, ordered_frames)]

        print(subslices)
        
        self.reset_renderers()
        self.running_renderers = []
        self.completed_renderers = []

        #logfile = filepath.parent.joinpath(f"{filepath.stem}-log.txt")
        #log = open(logfile, "w")

        for subslice in subslices:
            print("slice >", len(subslice))
            if len(subslice) == 0:
                continue
            sargs = [
                "coldtype",
                sys.argv[1],
                "-i", ",".join([str(s) for s in subslice]),
                "-isp",
                "-s", str(self.args.scale),
            ]
            r = self.args.rasterizer
            if r:
                sargs.append("-r", r)
            if self.args.no_sound:
                sargs.append("-ns")
            if self.args.cpu_render or skia is None:
                sargs.append("-cpu")
            #print(sys.argv)
            #print(sargs)
            #return
            renderer = Popen(sargs) #stdout=log)
            self.running_renderers.append(renderer)
        
        while self.running_renderers.count(None) != len(self.running_renderers):
            for idx, renderer in enumerate(self.running_renderers):
                if renderer:
                    retcode = renderer.poll()
                    if retcode == 5:
                        self.running_renderers[idx] = None
            ptime.sleep(.1)

        print("TIME >>>", ptime.time() - start)
        if not self.args.no_sound:
            os.system("afplay /System/Library/Sounds/Frog.aiff")
    
    def rasterize(self, content, render, path):
        if render.self_rasterizing:
            print("Self rasterizing")
            return
        
        scale = int(self.args.scale)
        rasterizer = self.args.rasterizer or render.rasterizer

        if rasterizer == "drawbot":
            from coldtype.pens.drawbotpen import DrawBotPen
            DrawBotPen.Composite(content, render.rect, str(path), scale=scale)
        elif rasterizer == "skia":
            if not skia:
                raise Exception("pip install skia-python")
            if render.fmt == "png":
                content = content.precompose(render.rect)
                render.last_result = content
                if render.bg_render:
                    content = DATPens([
                        DATPen().rect(render.rect).f(render.bg),
                        content
                    ])
                SkiaPen.Composite(content, render.rect, str(path), scale=scale, context=None if self.args.cpu_render else self.context, style=render.style)
            elif render.fmt == "pdf":
                SkiaPen.PDFOnePage(content, render.rect, str(path), scale=scale)
            elif render.fmt == "svg":
                SkiaPen.SVG(content, render.rect, str(path), scale=scale)
            else:
                print("> Skia render not supported for ", render.fmt)
        elif rasterizer == "svg":
            path.write_text(SVGPen.Composite(content, render.rect, viewBox=render.viewBox))
        elif rasterizer == "pickle":
            pickle.dump(content, open(path, "wb"))
        else:
            raise Exception(f"rasterizer ({rasterizer}) not supported")
    
    def reload_and_render(self, trigger, watchable=None, indices=None):
        #self.playing = 0

        if self.args.is_subprocess and not self.args.cpu_render:
            if not glfw.init():
                raise RuntimeError('glfw.init() failed')
            glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
            glfw.window_hint(glfw.STENCIL_BITS, 8)
            window = glfw.create_window(640, 480, '', None, None)
            glfw.make_context_current(window)
            self.context = skia.GrDirectContext.MakeGL()
            print("SUB GLFW")

        wl = len(self.watchees)
        self.window_scrolly = 0

        try:
            should_halt = self.reload(trigger)
            if should_halt:
                return True
            if self.program:
                preview_count, render_count = self.render(trigger, indices=indices)
                if self.args.show_render_count:
                    print("render>", preview_count, "/", render_count)
                if self.playing < 0:
                    self.playing = 1
            else:
                print(">>>>>>>>>>>> No program loaded! <<<<<<<<<<<<<<")
        except:
            self.show_error()

        if wl < len(self.watchees) and len(self.observers) > 0:
            pprint(self.watchees)
            self.stop_watching_file_changes()
            self.watch_file_changes()

    def main(self):
        if self.dead:
            return

        if self.args.memory:
            tracemalloc.start(10)
            self._last_memory = -1
        try:
            #asyncio.get_event_loop().run_until_complete(self.start())
            self.start()
        except KeyboardInterrupt:
            #print("INTERRUPT")
            self.on_exit()
        if self.args.show_exit_code:
            print("exit>", self.exit_code)
        sys.exit(self.exit_code)
    
    def set_title(self, text):
        if glfw and not self.args.no_viewer:
            glfw.set_window_title(self.window, text)
    
    def get_content_scale(self):
        u_scale = self.py_config.get("WINDOW_SCALE")
        
        if self.args.window_content_scale == None:
            if u_scale:
                return u_scale
            elif glfw and not self.args.no_viewer:
                return glfw.get_window_content_scale(self.window)[0]
            else:
                return 1
        else:
            return self.args.window_content_scale
    
    def initialize_gui_and_server(self):
        if self.args.websocket_external:
            self.state.external_url = f"ws://{self.args.websocket_external}"
            print(self.state.external_url)

        if self.args.websocket or self.args.webviewer:
            global WEBSOCKET_PORT
            WEBSOCKET_PORT = self.args.port
            try:
                print("WEBSOCKET>", f"localhost:{WEBSOCKET_PORT}")
                self.server = echo_server(WEBSOCKET_PORT)
                daemon = threading.Thread(name="daemon_websocket", target=self.server.serveforever)
                daemon.setDaemon(True)
                daemon.start()
            except OSError:
                self.server = None
        else:
            self.server = None
        
        if self.args.webviewer:
            port = self.args.webviewer_port
            if port != 0:
                print("WEBVIEWER>", f"localhost:{port}")

                def start_server(port):
                    httpd = HTTPServer(('', port), WebViewerHandler)
                    httpd.serve_forever()

                daemon = threading.Thread(name='daemon_server',
                    target=start_server, args=(port,))
                daemon.setDaemon(True)
                daemon.start()
        elif not glfw and not skia:
            print("\n\n>>> To view a coldtype program, you either need to install with the [viewer] optional package, or run coldtype in --webviewer mode (aka -wv)\n\n")

        if glfw and not self.args.no_viewer:
            if not glfw.init():
                raise RuntimeError('glfw.init() failed')
            glfw.window_hint(glfw.STENCIL_BITS, 8)
            
            self.transparent = self.py_config.get("WINDOW_TRANSPARENT", self.args.window_transparent)
            if self.transparent:
                glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
                glfw.window_hint(glfw.DECORATED, glfw.FALSE)
            else:
                glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.FALSE)
            
            self.passthrough = self.py_config.get("WINDOW_PASSTHROUGH", self.args.window_passthrough)
            if self.passthrough:
                try:
                    glfw.window_hint(0x0002000D, glfw.TRUE)
                    #glfw.window_hint(glfw.MOUSE_PASSTHROUGH, glfw.TRUE)
                except glfw.GLFWError:
                    print("failed to hint window for mouse-passthrough")

            if self.py_config.get("WINDOW_BACKGROUND"):
                glfw.window_hint(glfw.FOCUSED, glfw.FALSE)
            
            if self.py_config.get("WINDOW_FLOAT", self.args.window_float):
                glfw.window_hint(glfw.FLOATING, glfw.TRUE)

            self.window = glfw.create_window(int(50), int(50), '', None, None)
            self.window_scrolly = 0

            recp = sibling(__file__, "../../assets/RecMono-CasualItalic.ttf")
            self.typeface = skia.Typeface.MakeFromFile(str(recp))
            #print(self.typeface.serialize().bytes().decode("utf-8"))
            
            o = self.py_config.get("WINDOW_OPACITY", 1)
            if self.args.window_opacity is not None:
                o = self.args.window_opacity
            glfw.set_window_opacity(self.window, max(0.1, min(1, o)))

            self._prev_scale = self.get_content_scale()
            
            glfw.make_context_current(self.window)
            glfw.set_key_callback(self.window, self.on_key)
            glfw.set_char_callback(self.window, self.on_character)
            glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
            glfw.set_cursor_pos_callback(self.window, self.on_mouse_move)
            glfw.set_scroll_callback(self.window, self.on_scroll)

            #if primary_monitor:
            #    glfw.set_window_monitor(self.window, primary_monitor, 0, 0, int(50), int(50))

        try:
            midiin = rtmidi.RtMidiIn()
            lookup = {}
            self.midis = []
            for p in range(midiin.getPortCount()):
                lookup[midiin.getPortName(p)] = p

            for device, mapping in self.midi_mapping.items():
                if device in lookup:
                    mapping["port"] = lookup[device]
                    mi = rtmidi.RtMidiIn()
                    mi.openPort(lookup[device])
                    self.midis.append([device, mi])
                else:
                    if self.args.midi_info:
                        print(f">>> no midi port found with that name ({device}) <<<")
        except:
            self.midis = []
        
        if skia and glfw and not self.args.no_viewer:
            self.context = skia.GrDirectContext.MakeGL()
        else:
            self.context = None

        #self.watch_file_changes()

        if len(self.watchees) > 0:
            self.set_title(self.watchees[0][1].name)
        else:
            self.set_title("coldtype")

        self.hotkeys = None
        try:
            if self.hotkey_mapping:
                from pynput import keyboard
                mapping = {}
                for k, v in self.hotkey_mapping.items():
                    mapping[k] = partial(self.on_hotkey, k, v)
                #self.hotkeys = keyboard.GlobalHotKeys({
                #    "<cmd>+<f8>": self.on_hotkey
                #})
                self.hotkeys = keyboard.GlobalHotKeys(mapping)
                self.hotkeys.start()
        except:
            pass
    
        if pyaudio:
            self.paudio = pyaudio.PyAudio()
            self.paudio_source:soundfile.SoundFile = None
            self.paudio_stream = None
            self.paudio_rate = 0
    
        if self.args.sidecar:
            if self.args.sidecar == ".":
                self.args.sidecar = self.filepath
            dst = DataSourceThread(Path(self.args.sidecar).expanduser().resolve())
            dst.start()
            self.sidecar_threads.append(dst)
        
        if self.args.tails:
            ts = self.args.tails.split(",")
            for t in ts:
                if t in ["rf", "robofont"]:
                    t = "~/Library/Application Support/RoboFont/robofont-3-py3.log"
                tp = Path(t.strip()).expanduser().absolute()
                proc = Popen(["tail", "-f", str(tp)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                t = threading.Thread(target=show_tail, args=(proc,), daemon=True)
                t.start()
                self.tails.append(t)

    def start(self):
        if self.args.midi_info:
            try:
                midiin = rtmidi.RtMidiIn()
                ports = range(midiin.getPortCount())
                for p in ports:
                    print(p, midiin.getPortName(p))
            except:
                print("Please run `pip install rtmidi` in your venv")
                self.on_exit()
                return
            if self.args.no_watch:
                should_halt = True
            else:
                should_halt = self.before_start()
        else:
            should_halt = self.before_start()
        
        if not self.args.no_watch:
            self.initialize_gui_and_server()
        else:
            self.window = None
            self.server = None
        
        if should_halt:
            self.on_exit()
        else:
            if self.args.all:
                self.reload_and_render(Action.RenderAll)
            elif self.args.indices:
                indices = [int(x.strip()) for x in self.args.indices.split(",")]
                self.reload_and_render(Action.RenderIndices, indices=indices)
            else:
                should_halt = self.reload_and_render(Action.Initial)
                if should_halt:
                    self.on_exit()
                    return
            self.on_start()
            if not self.args.no_watch:
                if glfw and not self.args.no_viewer:
                    self.listen_to_glfw()
                elif self.args.webviewer:
                    while True:
                        self.turn_over()
                        sleep(0.25)
            else:
                self.on_exit()
    
    def before_start(self):
        pass

    def on_start(self):
        pass

    def on_request_from_render(self, render, request, action=None):
        print("request (noop)>", render, request, action)

    def on_hotkey(self, key_combo, action):
        print("HOTKEY", key_combo)
        self.action_waiting = action
    
    def on_message(self, message, action):
        if action:
            enum_action = self.lookup_action(action)
            if enum_action:
                print(">", enum_action)
                self.action_waiting = enum_action
                #self.on_action(enum_action, message)
            else:
                print(">>> (", action, ") is not a recognized action")
    
    def jump_to_fn(self, fn_name):
        if self.last_animation:
            fi = self.last_animation.fn_to_frame(fn_name)
            if fi is None:
                print("fn_to_frame: no match")
                return False
            #self.last_animation.storyboard = [fi]
            self.state.adjust_all_frame_offsets(0, absolute=True)
            self.state.adjust_keyed_frame_offsets(
                self.last_animation.name, lambda i, o: fi)
            self.action_waiting = Action.PreviewStoryboard
            return True
    
    def on_remote_command(self, cmd, context):
        #print(">>>>>", cmd, context)
        try:
            kbs = KeyboardShortcut(cmd)
            if kbs:
                self.on_shortcut(kbs)
                return
        except ValueError:
            pass

        if context:
            if cmd == "show_function":
                lines = self.codepath.read_text().split("\n")
                lidx = int(context)
                lidx += self._codepath_offset
                line = lines[lidx]
                while not line.startswith("@"):
                    lidx -= 1
                    line = lines[lidx]
                fn_name = lines[lidx+1].strip("def ").split("(")[0].strip()
                self.jump_to_fn(fn_name)
        else:
            if cmd == "∑":
                self.state.exit_keylayer()
                self.action_waiting = Action.PreviewStoryboard
                return
            if self.state.keylayer == Keylayer.Cmd:
                self.state.keybuffer = cmd
                self.action_waiting = Action.PreviewStoryboard
                return

            mods = [0, 0, 0, 0]
            char = None
            i = 0
            while i < len(cmd):
                c = cmd[i]
                if c == "∆": # shift
                    mods[2] = 1
                elif c == "˚": # control
                    mods[3] = 1
                elif c == "¬": # alt
                    mods[1] = 1
                elif c == "…": # super
                    mods[0] = 1
                elif c == "∑":
                    char = glfw.KEY_ESCAPE
                else:
                    char = ord(c.upper())
                i += 1
            
            #print(">", cmd, context, char, mods)
            if char:
                self.on_potential_shortcut(char, glfw.PRESS, mods)

    def lookup_action(self, action):
        try:
            return Action(action)
        except ValueError:
            try:
                return EditAction(action)
            except ValueError:
                return None
    
    def additional_actions(self):
        return []
    
    def on_scroll(self, win, xoff, yoff):
        self.window_scrolly += yoff
        #self.on_action(Action.PreviewStoryboard)
        #print(xoff, yoff)
        #pass # TODO!
    
    def on_release(self):
        release_fn = self.release_fn()
        if not release_fn:
            print("No `release` fn defined in source")
            return
        trigger = Action.RenderAll
        renders = self.renderables(trigger)
        output_folder = None
        all_passes = []
        try:
            for render in renders:
                if not render.preview_only:
                    output_folder, prefix, fmt, passes = self.add_paths_to_passes(trigger, render, [0])
                    for rp in passes:
                        all_passes.append(rp)

            release_fn(all_passes)
        except Exception as e:
            stack = traceback.format_exc()
            print(stack)
            print("Release failed", str(e))
    
    def allow_mouse(self):
        return True
        #return self.state.keylayer == Keylayer.Editing
    
    def on_mouse_button(self, _, btn, action, mods):
        if not self.allow_mouse():
            return
        
        pos = Point(glfw.get_cursor_pos(self.window)).scale(2) # TODO should this be preview-scale?
        pos[1] = self.last_rect.h - pos[1]
        requested_action = self.state.on_mouse_button(pos, btn, action, mods)
        if requested_action:
            self.action_waiting = requested_action
    
    def on_mouse_move(self, _, xpos, ypos):
        if not self.allow_mouse():
            return
        
        pos = Point((xpos, ypos)).scale(2)
        pos[1] = self.last_rect.h - pos[1]
        requested_action = self.state.on_mouse_move(pos)
        if requested_action:
            self.action_waiting = requested_action

    def on_character(self, _, codepoint):
        if self.state.keylayer != Keylayer.Default:
            if self.state.keylayer_shifting:
                self.state.keylayer_shifting = False
                self.on_action(Action.PreviewStoryboard)
                return
            requested_action = self.state.on_character(codepoint)
            if requested_action:
                self.action_waiting = requested_action
            
    def shortcuts(self):
        if not glfw:
            return {}
        keyed = {}
        for k, v in SHORTCUTS.items():
            modded = []
            for mods, symbol in v:
                #print([symbol_to_glfw(s) for s in mods])
                modded.append([[symbol_to_glfw(s) for s in mods], symbol_to_glfw(symbol)])
            keyed[k] = modded
        return keyed
    
    def repeatable_shortcuts(self):
        return REPEATABLE_SHORTCUTS
    
    def shortcut_to_action(self, shortcut):
        if shortcut in self.repeatable_shortcuts():
            self.paudio_preview = 1
        
        if shortcut == KeyboardShortcut.PreviewPrevMany:
            return Action.PreviewStoryboardPrevMany
        elif shortcut == KeyboardShortcut.PreviewPrev:
            return Action.PreviewStoryboardPrev
        elif shortcut == KeyboardShortcut.PreviewNextMany:
            return Action.PreviewStoryboardNextMany
        elif shortcut == KeyboardShortcut.PreviewNext:
            return Action.PreviewStoryboardNext
        
        elif shortcut == KeyboardShortcut.JumpHome:
            self.state.adjust_all_frame_offsets(0, absolute=True)
        elif shortcut == KeyboardShortcut.JumpEnd:
            self.state.adjust_all_frame_offsets(-1, absolute=True)
        
        elif shortcut == KeyboardShortcut.JumpPrev:
            self.state.adjust_keyed_frame_offsets(
                self.last_animation.name,
                lambda i, o: self.last_animation.jump(o, -1))
        elif shortcut == KeyboardShortcut.JumpNext:
            self.state.adjust_keyed_frame_offsets(
                self.last_animation.name,
                lambda i, o: self.last_animation.jump(o, +1))
        elif shortcut == KeyboardShortcut.JumpStoryboard:
            self.state.adjust_keyed_frame_offsets(
                self.last_animation.name,
                lambda i, o: self.last_animation.storyboard[i])

        elif shortcut == KeyboardShortcut.ClearLastRender:
            return Action.ClearLastRender
        elif shortcut == KeyboardShortcut.ClearRenderedFrames:
            return Action.ClearRenderedFrames
        
        elif shortcut == KeyboardShortcut.PlayRendered:
            self.paudio_preview = 1
            self.on_action(Action.RenderedPlay)
            return -1
        elif shortcut == KeyboardShortcut.PlayPreview:
            self.paudio_preview = 1
            self.playing_preloaded_frame = -1
            return Action.PreviewPlay
        elif shortcut == KeyboardShortcut.PlayPreviewSlow:
            if shortcut not in self.recurring_actions:
                self.recurring_actions[shortcut] = dict(
                    interval=0.5,
                    action=KeyboardShortcut.PreviewNext,
                    last=0)
            else:
                del self.recurring_actions[shortcut]
        elif shortcut == KeyboardShortcut.PlayAudioFrame:
            self.paudio_preview = 1
        
        elif shortcut == KeyboardShortcut.ReloadSource:
            return Action.PreviewStoryboardReload
        elif shortcut == KeyboardShortcut.RestartApp:
            self.on_action(Action.RestartRenderer)
            return -1
        elif shortcut == KeyboardShortcut.Quit:
            self.dead = True
            return -1
        
        elif shortcut == KeyboardShortcut.Release:
            self.on_action(Action.Release)
            return -1
        elif shortcut == KeyboardShortcut.RenderAll:
            self.on_action(Action.RenderAll)
            return -1
        elif shortcut == KeyboardShortcut.RenderWorkarea:
            self.on_action(Action.RenderWorkarea)
            return -1
        elif shortcut == KeyboardShortcut.ToggleMultiplex:
            self.on_action(Action.ToggleMultiplex)
            return -1
        
        elif shortcut == KeyboardShortcut.KeylayerEditing:
            self.state.keylayer = Keylayer.Editing
            self.state.keylayer_shifting = True
            return -1
        elif shortcut == KeyboardShortcut.KeylayerCmd:
            self.state.keylayer = Keylayer.Cmd
            self.state.keylayer_shifting = True
        elif shortcut == KeyboardShortcut.KeylayerText:
            if self.last_animation:
                fi = self.last_animation._active_frames(self.state)[0]
                txt = self.last_animation.timeline.text_for_frame(fi)
                if txt:
                    self.state.keybuffer = list(txt)
            self.state.keylayer = Keylayer.Text
            self.state.keylayer_shifting = True
        
        elif shortcut == KeyboardShortcut.OverlayInfo:
            self.state.toggle_overlay(Overlay.Info)
        elif shortcut == KeyboardShortcut.OverlayTimeline:
            self.state.toggle_overlay(Overlay.Timeline)
        
        elif shortcut == KeyboardShortcut.PreviewScaleUp:
            self.state.mod_preview_scale(+0.1)
        elif shortcut == KeyboardShortcut.PreviewScaleDown:
            self.state.mod_preview_scale(-0.1)
        elif shortcut == KeyboardShortcut.PreviewScaleMin:
            self.state.mod_preview_scale(0, 0.1)
        elif shortcut == KeyboardShortcut.PreviewScaleMax:
            self.state.mod_preview_scale(0, 5)
        elif shortcut == KeyboardShortcut.PreviewScaleDefault:
            self.state.mod_preview_scale(0, 1)

        elif shortcut == KeyboardShortcut.WindowOpacityDown:
            o = glfw.get_window_opacity(self.window)
            glfw.set_window_opacity(self.window, min(1, o-0.1))
        elif shortcut == KeyboardShortcut.WindowOpacityUp:
            o = glfw.get_window_opacity(self.window)
            glfw.set_window_opacity(self.window, min(1, o+0.1))
        elif shortcut == KeyboardShortcut.WindowOpacityMin:
            glfw.set_window_opacity(self.window, 0.1)
        elif shortcut == KeyboardShortcut.WindowOpacityMax:
            glfw.set_window_opacity(self.window, 1)
        
        elif shortcut == KeyboardShortcut.MIDIControllersPersist:
            self.state.persist()
        elif shortcut == KeyboardShortcut.MIDIControllersClear:
            self.state.clear()
        elif shortcut == KeyboardShortcut.MIDIControllersReset:
            self.state.reset(ignore_current_state=True)
        
        elif shortcut == KeyboardShortcut.JumpToFrameFunctionDef:
            frame = self.last_animation._active_frames(self.state)[0]
            self.send_to_external("jump_to_def", info=self.last_animation.frame_to_fn(frame))
    
    def on_shortcut(self, shortcut):
        waiting = self.shortcut_to_action(shortcut)
        if waiting:
            if waiting != -1:
                self.action_waiting = waiting
        else:
            self.action_waiting = Action.PreviewStoryboard
    
    def on_potential_shortcut(self, key, action, mods):
        for shortcut, options in self.shortcuts().items():
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
                
                #print(shortcut, mod_matches, all(mod_matches))
                mod_match = all(mod_matches)
                
                if not mod_match and len(modifiers) == 0 and isinstance(mods, list):
                    mod_match = True
                
                if len(modifiers) == 0 and mods != 0 and not isinstance(mods, list):
                    mod_match = False
                
                if mod_match and key == skey:
                    if (action == glfw.REPEAT and shortcut in self.repeatable_shortcuts()) or action == glfw.PRESS:
                        #print(shortcut, modifiers, skey, mod_match)
                        return self.on_shortcut(shortcut)

    def on_key(self, win, key, scan, action, mods):
        if self.state.keylayer != Keylayer.Default:
            requested_action = self.state.on_key(win, key, scan, action, mods)
            if requested_action:
                self.action_waiting = requested_action
            return
        
        self.on_potential_shortcut(key, action, mods)
        
    def preview_audio(self, frame=None):
        #if not self.args.preview_audio:
        #    return
        
        if pyaudio and self.paudio_source:
            hz = self.paudio_source.samplerate
            width = self.paudio_source.channels

            if not self.paudio_stream or hz != self.paudio_rate:
                self.paudio_rate = hz
                self.paudio_stream = self.paudio.open(
                    format=pyaudio.paFloat32,
                    channels=width,
                    rate=hz,
                    output=True)

            if frame is None:
                audio_frame = self.last_animation._active_frames(self.state)[0]
            else:
                audio_frame = frame
            chunk = int(hz / self.last_animation.timeline.fps)

            try:
                self.paudio_source.seek(chunk*audio_frame)
                data = self.paudio_source.read(chunk)
                data = data.astype(np.float32).tostring()
                self.paudio_stream.write(data)
            except wave.Error:
                print(">>> Could not read audio at frame", audio_frame)
    
    def stdin_to_action(self, stdin):
        action_abbrev, *data = stdin.split(" ")
        if action_abbrev == "ps":
            self.state.preview_scale = max(0.1, min(5, float(data[0])))
            return Action.PreviewStoryboard, None
        elif action_abbrev == "a":
            return Action.RenderAll, None
        elif action_abbrev == "w":
            return Action.RenderWorkarea, None
        elif action_abbrev == "pf":
            return Action.PreviewIndices, [int(i.strip()) for i in data]
        elif action_abbrev == "r":
            return Action.RestartRenderer, None
        elif action_abbrev == "l":
            return Action.Release, None
        elif action_abbrev == "m":
            return Action.ToggleMultiplex, None
        elif action_abbrev == "rp":
            self.reset_filepath(data[0])
            return Action.Resave, None
        elif action_abbrev == "ff":
            self.function_filters = data
            return Action.PreviewStoryboard, None
        else:
            enum_action = self.lookup_action(action_abbrev)
            if enum_action:
                return enum_action, None
            else:
                return None, None

    def on_stdin(self, stdin):
        if self.jump_to_fn(stdin):
            return
        action, data = self.stdin_to_action(stdin)
        if action:
            if action == Action.PreviewIndices:
                self.render(action, indices=data)
            elif action == Action.RestartRenderer:
                self.on_exit(restart=True)
            else:
                self.on_action(action)

    def on_action(self, action, message=None) -> bool:
        #if action != Action.PreviewStoryboardNext:
        #    print("ACTION", action)

        if action in [Action.RenderAll, Action.RenderWorkarea, Action.PreviewStoryboardReload]:
            self.reload_and_render(action)
            return True
        elif action in [Action.PreviewStoryboard]:
            self.render(Action.PreviewStoryboard)
        elif action in [
            Action.PreviewStoryboardNextMany,
            Action.PreviewStoryboardPrevMany,
            Action.PreviewStoryboardNext,
            Action.PreviewStoryboardPrev,
            Action.PreviewPlay]:
            if action == Action.PreviewPlay:
                self.playing_preloaded_frame = -1
                if self.playing == 0:
                    self.playing = 1
                else:
                    self.playing = 0
            if action == Action.PreviewStoryboardPrevMany:
                self.state.adjust_all_frame_offsets(-self.many_increment)
            elif action == Action.PreviewStoryboardPrev:
                self.state.adjust_all_frame_offsets(-1)
            elif action == Action.PreviewStoryboardNextMany:
                self.state.adjust_all_frame_offsets(+self.many_increment)
            elif action == Action.PreviewStoryboardNext:
                self.state.adjust_all_frame_offsets(+1)
            self.render(Action.PreviewStoryboard)
        elif action == Action.RenderedPlay:
            self.playing = 0
            if self.playing_preloaded_frame >= 0:
                self.playing_preloaded_frame = -1
                self.preloaded_frames = []
            else:
                anm = self.animation()
                passes = self.add_paths_to_passes(Action.RenderAll, anm, anm.all_frames())[-1]
                self.preload_frames(passes)
        elif action == Action.Release:
            self.on_release()
        elif action == Action.ArbitraryCommand:
            self.on_stdin(message.get("input"))
            return True
        elif action == Action.RestartRenderer:
            self.on_exit(restart=True)
        elif action == Action.Kill:
            os.kill(os.getpid(), signal.SIGINT)
            #self.on_exit(restart=False)
        elif action == Action.ToggleMultiplex:
            self.multiplexing = not self.multiplexing
            print(">>> MULTIPLEXING?", self.multiplexing)
        elif action == Action.ClearLastRender:
            for r in self.renderables(Action.PreviewStoryboard):
                r.last_result = None
            self.action_waiting = Action.PreviewStoryboard
        elif action == Action.ClearRenderedFrames:
            for r in self.renderables(Action.PreviewStoryboard):
                shutil.rmtree(r.output_folder, ignore_errors=True)
            print("Deleted rendered version")
        elif message.get("serialization"):
            ptime.sleep(0.5)
            self.reload(Action.Resave)
            print(">>>>>>>>>>>", self.animation().timeline.cti)
            cw = self.animation().timeline.find_workarea()
            print("WORKAREA", cw)
            if cw:
                start, end = cw
                self.send_to_external(None, workarea_update=True, start=start, end=end)
            else:
                print("No CTI/trackGroups found")
        elif action in EditAction:
            if action in [EditAction.SelectWorkarea]:
                self.send_to_external(action, serialization_request=True)
            else:
                self.send_to_external(action, edit_action=True)
        else:
            return False
    
    def send_to_external(self, action, **kwargs):
        if not self.server:
            return

        if action in ["save", "jump_to_def"]:
            for _, client in self.server.connections.items():
                client.sendMessage(json.dumps({"midi_shortcut":action, "file":str(self.filepath), **kwargs}))
            return
        
        animation = self.animation()
        if animation and animation.timeline:
            print("EVENT", action, kwargs)
            if action:
                kwargs["action"] = action.value
            kwargs["prefix"] = self.filepath.stem
            kwargs["fps"] = animation.timeline.fps
            for _, client in self.server.connections.items():
                client.sendMessage(json.dumps(kwargs))
    
    def process_ws_message(self, message):
        try:
            jdata = json.loads(message)
            if "webviewer" in jdata:
                self.action_waiting = Action.PreviewStoryboard
                return

            action = jdata.get("action")
            if action:
                self.on_message(jdata, jdata.get("action"))
            elif jdata.get("metadata") and jdata.get("path"):
                path = Path(jdata.get("path"))
                if path == self.filepath:
                    if self.args.monitor_lines:
                        self.line_number = jdata.get("line_number")
            elif jdata.get("command"):
                cmd = jdata.get("command")
                context = jdata.get("context")
                self.on_remote_command(cmd, context)
            elif jdata.get("rendered") is not None:
                idx = jdata.get("rendered")
                print("IDX>>>>>>>", idx)
                self.state.adjust_keyed_frame_offsets(
                    self.last_animation.name,
                    lambda i, o: idx)
                self.action_waiting = Action.PreviewStoryboard
                
        #except TypeError:
        #    raise TypeError("Huh")
        except:
            self.show_error()
            print("Malformed message")
    
    def listen_to_glfw(self):
        should_close = False
        should_close = glfw.window_should_close(self.window)
        while not self.dead and not should_close:
            scale_x = self.get_content_scale()
            if scale_x != self._prev_scale:
                self._prev_scale = scale_x
                self.on_action(Action.PreviewStoryboard)
            
            if self._should_reload:
                self._should_reload = False
                self.on_action(Action.PreviewStoryboard)
            
            t = glfw.get_time()
            td = t - self.glfw_last_time

            spf = 0.1
            if self.last_animation:
                spf = 1 / float(self.last_animation.timeline.fps)

                if td >= spf:
                    self.glfw_last_time = t
                else:
                    glfw.poll_events()
                    continue

            if self.last_animation and self.playing_preloaded_frame >= 0 and len(self.preloaded_frames) > 0:
                GL.glClear(GL.GL_COLOR_BUFFER_BIT)

                with self.surface as canvas:
                    path = self.preloaded_frames[self.playing_preloaded_frame]
                    c = self.last_animation.bg
                    canvas.clear(c.skia())
                    image = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(path)))
                    canvas.drawImage(image, 0, 0)
                
                self.surface.flushAndSubmit()
                glfw.swap_buffers(self.window)

                self.preview_audio(frame=(self.playing_preloaded_frame+1)%len(self.preloaded_frames))

                self.playing_preloaded_frame += 1
                if self.playing_preloaded_frame == len(self.preloaded_frames):
                    self.playing_preloaded_frame = 0
                ptime.sleep(0.01)
            else:
                ptime.sleep(0.025)
                self.glfw_last_time = t
                self.turn_over()
                global last_line
                if self.state.cmd:
                    cmd = self.state.cmd
                    self.state.reset_keystate()
                    self.on_stdin(cmd)
                elif last_line:
                    self.on_stdin(last_line.strip())
                    last_line = None
                
                #if self.playing != 0:
                    #self.action_waiting = Action.PreviewStoryboardNext
                    #self.on_action(Action.PreviewStoryboardNext)
            
            self.state.reset_keystate()
            glfw.poll_events()
        self.on_exit(restart=False)
    
    def preview_scale(self):
        return self.state.preview_scale
    
    def create_surface(self, rect):
        #print("NEW SURFACE", rect)
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
    
    def turn_over_webviewer(self):
        renders = []
        try:
            title = self.watchees[0][1].name
        except:
            title = "coldtype"

        for idx, (render, result, rp) in enumerate(self.previews_waiting_to_paint):
            if self.args.format == "canvas":
                renders.append(dict(fmt="canvas", jsonpen=JSONPen.Composite(result, render.rect), rect=[*render.rect], bg=[*render.bg]))
            else:
                renders.append(dict(fmt="svg", svg=SVGPen.Composite(result, render.rect, viewBox=render.viewBox), rect=[*render.rect], bg=[*render.bg]))
    
        if renders:
            for _, client in self.server.connections.items():
                if hasattr(client, "webviewer") and client.webviewer:
                    client.sendMessage(json.dumps({"renders":renders, "title":title}))
    
    def turn_over_glfw(self):
        dscale = self.preview_scale()
        rects = []

        render_previews = len(self.previews_waiting_to_paint) > 0
        if not render_previews:
            return

        if render_previews:
            if pyaudio and self.paudio_source:
                if self.paudio_preview == 1:
                    self.preview_audio()
                    if self.playing == 0:
                        self.paudio_preview = 0

        w = 0
        llh = -1
        lh = -1
        h = 0
        for render, result, rp in self.previews_waiting_to_paint:
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
        if frect != self.last_rect:
            self.create_surface(frect)

        if not self.last_rect or frect != self.last_rect:
            m_scale = self.get_content_scale()
            scale_x, scale_y = m_scale, m_scale
            
            #if not DARWIN:
            #    scale_x, scale_y = 1.0, 1.0

            ww = int(w/scale_x)
            wh = int(h/scale_y)
            glfw.set_window_size(self.window, ww, wh)

            pin = self.py_config.get("WINDOW_PIN", None)
            if self.args.window_pin:
                pin = self.args.window_pin
            
            if not isinstance(pin, str):
                print("--window-pin must be compass direction")
                pin = "NE"

            primary_monitor = None
            if self.args.monitor_name:
                remn = self.args.monitor_name
                monitors = glfw.get_monitors()
                matches = []
                for monitor in monitors:
                    mn = glfw.get_monitor_name(monitor)
                    print(">>> MONITOR >>>", mn)
                    if remn in str(mn):
                        matches.append(monitor)
                if len(matches) > 0:
                    primary_monitor = matches[0]

            if pin:
                if primary_monitor:
                    monitor = primary_monitor
                else:
                    monitor = glfw.get_primary_monitor()
                work_rect = Rect(glfw.get_monitor_workarea(monitor))
                edges = Edge.PairFromCompass(pin)
                pinned = work_rect.take(ww, edges[0]).take(wh, edges[1]).round()
                if edges[1] == "mdy":
                    pinned = pinned.offset(0, -30)
                pinned = pinned.flip(work_rect.h+46)
                if self.args.window_pin_inset:
                    x, y = [int(n) for n in self.args.window_pin_inset.split(",")]
                    pinned = pinned.offset(-x, y)
                glfw.set_window_pos(self.window, pinned.x, pinned.y)
            else:
                glfw.set_window_pos(self.window, 0, 0)

        self.last_rect = frect

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        with self.surface as canvas:
            canvas.clear(skia.Color4f(0.3, 0.3, 0.3, 1))
            if self.transparent:
                canvas.clear(skia.Color4f(0.3, 0.3, 0.3, 0))
            
            for idx, (render, result, rp) in enumerate(self.previews_waiting_to_paint):
                rect = rects[idx].offset((w-rects[idx].w)/2, 0).round()
                try:
                    self.draw_preview(idx, dscale, canvas, rect, (render, result, rp))
                except Exception as e:
                    stack = traceback.format_exc()
                    print(stack)
                    paint = skia.Paint(AntiAlias=True, Color=skia.ColorRED)
                    canvas.drawString(stack.split("\n")[-2], 10, 32, skia.Font(None, 36), paint)
        
            if self.state.keylayer != Keylayer.Default and not self.args.hide_keybuffer:
                self.state.draw_keylayer(canvas, self.last_rect, self.typeface)
        
        self.surface.flushAndSubmit()
        glfw.swap_buffers(self.window)
    
    def turn_over(self):
        if self.dead:
            self.on_exit()
            return
        
        now = ptime.time()
        for k, v in self.watchee_mods.items():
            if v and (now - v) > 1:
                #print("CAUGHT ONE")
                self.action_waiting = Action.PreviewStoryboard
                self.watchee_mods[k] = None

        if self.action_waiting:
            action_in = self.action_waiting
            self.on_action(self.action_waiting)
            if action_in != self.action_waiting:
                # TODO should be recursive?
                self.on_action(self.action_waiting)
            self.action_waiting = None

        #if self.playing > 0:
        #    self.on_action(Action.PreviewStoryboardNext)
        
        if self.server:
            msgs = []
            for k, v in self.server.connections.items():
                if hasattr(v, "messages") and len(v.messages) > 0:
                    for msg in v.messages:
                        msgs.append(msg)
                        #self.process_ws_message(msg)
                    v.messages = []
            
            for msg in msgs:
                self.process_ws_message(msg)

        if not self.args.no_midi:
            self.monitor_midi()
        
        #if len(self.waiting_to_render) > 0:
        #    for action, path in self.waiting_to_render:
        #        self.reload_and_render(action, path)
        #    self.waiting_to_render = []
        
        if glfw and not self.args.no_viewer:
            self.turn_over_glfw()
        
        if self.args.webviewer:
            self.turn_over_webviewer()
        
        self.state.needs_display = 0
        self.previews_waiting_to_paint = []
    
        for render, request, action in self.requests_waiting:
            if action == "callback":
                self.action_waiting = Action.PreviewStoryboard
            else:
                self.on_request_from_render(render, request, action)
            self.requests_waiting = []

        if self.playing > 0:
            self.on_action(Action.PreviewStoryboardNext)
        
        for k, ra in self.recurring_actions.items():
            interval = ra.get("interval")
            if now - ra.get("last") > interval:
                ra["last"] = now
                print("RECURRING ACTION", k)
                self.on_shortcut(ra.get("action"))

    def draw_preview(self, idx, scale, canvas, rect, waiter):
        if isinstance(waiter[1], Path) or isinstance(waiter[1], str):
            image = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(waiter[1])))
            if image:
                canvas.drawImage(image, rect.x, rect.y)
            return
        
        render, result, rp = waiter
        error_color = coldtype.rgb(1, 1, 1).skia()
        canvas.save()
        canvas.translate(0, self.window_scrolly)
        canvas.translate(rect.x, rect.y)
        
        if not self.transparent:
            canvas.drawRect(skia.Rect(0, 0, rect.w, rect.h), skia.Paint(Color=render.bg.skia()))
        
        if not hasattr(render, "show_error"):
            canvas.scale(scale, scale)
        
        if render.clip:
            canvas.clipRect(skia.Rect(0, 0, rect.w, rect.h))
        
        #canvas.clear(coldtype.bw(0, 0).skia())
        #print("BG", render.func.__name__, render.bg)
        #canvas.clear(render.bg.skia())
        
        if render.direct_draw:
            try:
                render.run(rp, self.state, canvas)
            except Exception as e:
                stack = traceback.format_exc()
                print(stack)
                render.show_error = stack.split("\n")[-2]
                error_color = coldtype.rgb(0, 0, 0).skia()
        else:
            if self.args.composite or render.composites:
                comp = result.precompose(render.rect)
                render.last_result = comp
            else:
                comp = result
            render.draw_preview(1.0, canvas, render.rect, comp, rp)
        
        if hasattr(render, "blank_renderable"):
            paint = skia.Paint(AntiAlias=True, Color=coldtype.hsl(0, l=1, a=0.75).skia())
            canvas.drawString(f"{coldtype.__version__}", 359, 450, skia.Font(self.typeface, 42), paint)
            canvas.drawString("Nothing found", 297, 480, skia.Font(self.typeface, 24), paint)
        
        if hasattr(render, "show_error"):
            paint = skia.Paint(AntiAlias=True, Color=error_color)
            canvas.drawString(render.show_error, 30, 70, skia.Font(self.typeface, 50), paint)
            canvas.drawString("> See process in terminal for traceback", 30, 120, skia.Font(self.typeface, 32), paint)
        
        canvas.restore()
    
    def preload_frames(self, passes):
        for rp in passes:
            self.preloaded_frames.append(rp.output_path)
        self.playing_preloaded_frame = 0
    
    def on_modified(self, event):
        path = Path(event.src_path)
        #print("!", path)
        #return
        if path in self.watchee_paths():
            if path.suffix == ".json":
                last = self.watchee_mods.get(path)
                now = ptime.time()
                self.watchee_mods[path] = now
                if last is not None:
                    diff = now - last
                    if diff < 1:
                        #print("SKIP")
                        return
                    else:
                        #print("CONTINUE")
                        pass
                try:
                    json.loads(path.read_text())
                except json.JSONDecodeError:
                    print("Error decoding watched json", path)
                    #print(path.read_text())
                    return
            
            if path.suffix == ".py":
                try:
                    for render in self.renderables(Action.Resave):
                        for wr in render.watch_restarts:
                            if str(path) == str(wr):
                                importlib.reload(coldtype)
                                importlib.reload(coldtype.pens.datpen)
                                #self.action_waiting = Action.RestartRenderer
                except AttributeError:
                    pass
            
            idx = self.watchee_paths().index(path)
            wpath, wtype, wflag = self.watchees[idx]
            if wflag == "soft":
                self.state.watch_soft_mods[path] = True
                self.action_waiting = Action.PreviewStoryboard
                return

            try:
                print(f">>> resave: {Path(event.src_path).relative_to(Path.cwd())}")
            except:
                print(f">>> resave: {event.src_path}")
            
            if self.args.memory and process:
                memory = bytesto(process.memory_info().rss)
                diff = memory - self._last_memory
                self._last_memory = memory
                print(">>> pid:{:d}/new:{:04.2f}MB/total:{:4.2f}".format(os.getpid(), diff, memory))
            
            self.action_waiting = Action.PreviewStoryboardReload
            #self.waiting_to_render = [[Action.Resave, self.watchees[idx][0]]]

    def watch_file_changes(self):
        self.observers = []
        dirs = set([w[1].parent for w in self.watchees])
        for d in dirs:
            o = AsyncWatchdog(str(d), on_modified=self.on_modified, recursive=True)
            o.start()
            self.observers.append(o)
        if self.filepath:
            print(f"... watching {self.filepath.name} for changes ...")
        else:
            print(f"... no file specified, showing generic window ...")
    
    def monitor_midi(self):
        def execute_shortcut(shortcut):
            try:
                ksc = KeyboardShortcut(shortcut)
                ea = None
            except ValueError:
                ksc = None
                ea = EditAction(shortcut)
            
            if ksc:
                self.on_shortcut(KeyboardShortcut(shortcut))
            elif ea:
                self.on_action(EditAction(shortcut), {})

        controllers = {}
        for device, mi in self.midis:
            msg = mi.getMessage(0)
            while msg:
                if self.args.midi_info:
                    print(device, msg)
                if msg.isNoteOn(): # Maybe not forever?
                    nn = msg.getNoteNumber()
                    shortcut = self.midi_mapping[device]["note_on"].get(nn)
                    execute_shortcut(shortcut)
                if msg.isController():
                    cn = msg.getControllerNumber()
                    cv = msg.getControllerValue()
                    shortcut = self.midi_mapping[device].get("controller", {}).get(cn)
                    if shortcut:
                        if cv in shortcut:
                            print("shortcut!", shortcut, cv)
                            execute_shortcut(shortcut.get(cv))

                            #if self.server:
                            #    print("shortcut!", shortcut, cv)
                            #    self.send_to_external(shortcut[cv])
                    else:
                        controllers[device + "_" + str(cn)] = cv/127
                msg = mi.getMessage(0)
        
        if len(controllers) > 0:
            nested = {}
            for k, v in controllers.items():
                device, number = k.split("_")
                if not nested.get(device):
                    nested[device] = {}
                nested[device][str(number)] = v
            
            for device, numbers in nested.items():
                self.state.controller_values[device] = {**self.state.controller_values.get(device, {}), **numbers}

            self.action_waiting = Action.PreviewStoryboard
            #self.on_action(Action.PreviewStoryboard, {})
    
    def stop_watching_file_changes(self):
        for o in self.observers:
            o.stop()
        
    def reset_renderers(self):
        for r in self.running_renderers:
            if r:
                r.terminate()
    
    def restart(self):
        print("> RESTARTING...")
        args = sys.argv
        
        # attempt to preserve state across reload
        fo = str(self.state._frame_offsets)
        try:
            foi = args.index("-fo")
            args[foi+1] = fo
        except ValueError:
            args.append("-fo")
            args.append(fo)
        
        os.execl(sys.executable, *(["-m"]+args))

    def on_exit(self, restart=False):
        #if self.args.watch:
        #   print(f"<EXIT(restart:{restart})>")
        #if self.webviewer_thread:
        #    self.webviewer_thread.terminate()
        if glfw and not self.args.no_viewer:
            glfw.terminate()
        if self.context:
            self.context.abandonContext()
        if self.hotkeys:
            self.hotkeys.stop()
        self.reset_renderers()
        self.stop_watching_file_changes()

        if pyaudio:
            if hasattr(self, "paudio_stream") and self.paudio_stream:
                self.paudio_stream.stop_stream()
                self.paudio_stream.close()
            if hasattr(self, "paudio") and self.paudio:
                self.paudio.terminate()
            if hasattr(self, "paudio_source") and self.paudio_source:
                self.paudio_source.close()
        
        for t in self.sidecar_threads:
            t.should_run = False
        
        #for t in self.tails:
        #    t.terminate()
        
        if self.args.memory:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('traceback')

            # pick the biggest memory block
            stat = top_stats[0]
            print("%s memory blocks: %.1f KiB" % (stat.count, stat.size / 1024))
            for line in stat.traceback.format():
                print(line)
        
        if restart:
            self.restart()


def main():
    pargs, parser = Renderer.Argparser()
    Renderer(parser).main()

if __name__ == "__main__":
    main()