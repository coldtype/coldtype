import tempfile, traceback, threading
import argparse, importlib, inspect, json, math
import sys, os, re, signal, tracemalloc
import platform, pickle, string

import time as ptime
from pathlib import Path
from typing import Tuple
from pprint import pprint
from random import random
from runpy import run_path
from functools import partial
from subprocess import call, Popen
from random import shuffle, Random
from more_itertools import distribute
from docutils.core import publish_doctree

import skia, coldtype
from coldtype.helpers import *
from coldtype.geometry import Rect, Point
from coldtype.pens.skiapen import SkiaPen
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.renderable import renderable, Action, animation
from coldtype.renderer.watchdog import AsyncWatchdog
from coldtype.renderer.state import RendererState, Keylayer
from coldtype.renderer.utils import *

_random = Random()

import contextlib, glfw
from OpenGL import GL

try:
    import rtmidi
except ImportError:
    pass

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


class WebSocketThread(threading.Thread):
    def __init__(self, server):
        self.server = server
        self.should_run = True
        threading.Thread.__init__(self)
    
    def run(self):
        print("Running a server...")
        while self.should_run:
            self.server.serveonce()
            ptime.sleep(0.25)


class Renderer():
    def Argparser(name="coldtype", file=True, defaults={}, nargs=[]):
        parser = argparse.ArgumentParser(prog=name, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        
        if file:
            parser.add_argument("file", type=str, nargs="?", help="The source file for a coldtype render")
        for narg in nargs:
            parser.add_argument(narg[0], nargs="?", default=narg[1])
        
        pargs = dict(
            version=parser.add_argument("-v", "--version", action="store_true", default=False, help="Display version"),

            watch=parser.add_argument("-w", "--watch", action="store_true", default=True, help="Watch for changes to source files"),
            
            save_renders=parser.add_argument("-sv", "--save-renders", action="store_true", default=False, help="Should the renderer create image artifacts?"),
            
            rasterizer=parser.add_argument("-r", "--rasterizer", type=str, default=None, choices=["drawbot", "cairo", "svg", "skia", "pickle"], help="Which rasterization engine should coldtype use to create artifacts?"),

            cpu_render=parser.add_argument("-cpu", "--cpu-render", action="store_true", default=False, help="Should final rasters be performed without a GPU context?"),
            
            scale=parser.add_argument("-s", "--scale", type=float, default=1.0, help="When save-renders is engaged, what scale should images be rasterized at? (Useful for up-rezing)"),

            preview_scale=parser.add_argument("-ps", "--preview-scale", type=float, default=1.0, help="What size should previews be shown at?"),
            
            all=parser.add_argument("-a", "--all", action="store_true", default=False, help="If rendering an animation, pass the -a flag to render all frames sequentially"),

            multiplex=parser.add_argument("-mp", "--multiplex", action="store_true", default=False, help="Render in multiple processes"),

            memory=parser.add_argument("-m", "--memory", action="store_true", default=False, help="Show statistics about memory usage?"),

            midi_info=parser.add_argument("-mi", "--midi-info", action="store_true", default=False, help="Show available MIDI devices"),

            show_time=parser.add_argument("-st", "--show-time", action="store_true", default=False, help="Show time for each render"),

            is_subprocess=parser.add_argument("-isp", "--is-subprocess", action="store_true", default=False, help=argparse.SUPPRESS),

            thread_count=parser.add_argument("-tc", "--thread-count", type=int, default=defaults.get("thread_count", 8), help="How many threads when multiplexing?"),

            no_sound=parser.add_argument("-ns", "--no-sound", action="store_true", default=False, help="Don’t make sound"),
            
            format=parser.add_argument("-fmt", "--format", type=str, default=None, help="What image format should be saved to disk?"),

            layers=parser.add_argument("-l", "--layers", type=str, default=None, help="comma-separated list of layers to flag as renderable (if None, will flag all layers as renderable)"),

            indices=parser.add_argument("-i", "--indices", type=str, default=None),

            output_folder=parser.add_argument("-of", "--output-folder", type=str, default=None, help="If you don’t want to render to the default output location, specify that here."),

            monitor_lines=parser.add_argument("-ml", "--monitor-lines", action="store_true", default=False, help=argparse.SUPPRESS),

            filter_functions=parser.add_argument("-ff", "--filter-functions", type=str, default=None, help="Names of functions to render"),

            show_exit_code=parser.add_argument("-sec", "--show-exit-code", action="store_true", default=False, help=argparse.SUPPRESS),

            show_render_count=parser.add_argument("-src", "--show-render-count", action="store_true", default=False, help=argparse.SUPPRESS),

            disable_syntax_mods=parser.add_argument("-dsm", "--disable-syntax-mods", action="store_true", default=False, help="Coldtype has some optional syntax modifications that require copying the source to a new tempfile before running — would you like to skip this to preserve __file__ in your sources?")),
        return pargs, parser
    
    def read_configs(self):
        proj = Path(".coldtype.py")
        user = Path("~/.coldtype.py").expanduser()
        self.midi_mapping = {}
        self.hotkey_mapping = {}
        self.py_config = {}

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
                except Exception as e:
                    print("Failed to load config", p)
                    print("Exception:", e)

    def __init__(self, parser, no_socket_ok=False):
        sys.path.insert(0, os.getcwd())

        self.read_configs()

        self.args = parser.parse_args()
        if self.args.is_subprocess or self.args.all:
            self.args.watch = False
        
        self.disable_syntax_mods = self.args.disable_syntax_mods
        self.filepath = None
        self.state = RendererState(self)
        self.state.preview_scale = self.args.preview_scale

        self.observers = []
        self.watchees = []
        self.server_thread = None
        
        if not self.reset_filepath(self.args.file if hasattr(self.args, "file") else None):
            self.dead = True
            return
        else:
            self.dead = False
        
        monitor_stdin()
        
        if self.args.version:
            print(">>>", coldtype.__version__)
            self.dead = True
            return
        
        self.layers = [l.strip() for l in self.args.layers.split(",")] if self.args.layers else []

        self.program = None
        self.websocket = None
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

        if self.args.filter_functions:
            self.function_filters = [f.strip() for f in self.args.filter_functions.split(",")]
        else:
            self.function_filters = []
        self.multiplexing = self.args.multiplex
        self._should_reload = False
    
    def reset_filepath(self, filepath):
        self.line_number = -1
        self.stop_watching_file_changes()
        self.state.mouse = None
        self.state.frame_index_offset = 0

        if filepath:
            self.filepath = Path(filepath).expanduser().resolve()
            if self.filepath.suffix == ".py":
                if not self.filepath.exists(): # write some default code there after a prompt
                    print(">>> That python file does not exist...")
                    create = input(">>> Do you want to create it and add some coldtype boilerplate? (y/n): ")
                    if create.lower() == "y":
                        self.filepath.parent.mkdir(exist_ok=True, parents=True)
                        self.filepath.write_text("from coldtype import *\n\n@renderable()\ndef stub(r):\n    return (DATPen()\n        .oval(r.inset(50))\n        .f(0.8))\n")
            elif self.filepath.suffix == ".rst":
                if not self.filepath.exists():
                    print(">>> That rst file does not exist")
                    return False
            elif self.filepath.suffix == ".md":
                if not self.filepath.exists():
                    print(">>> That md file does not exist")
                    return False
            else:
                print(">>> Coldtype can only read .py, .rst, and .md files")
                return False
            self.codepath = None
            self.watchees = [[Watchable.Source, self.filepath]]
            if not self.args.is_subprocess:
                self.watch_file_changes()
        else:
            self.watchees = []
            self.filepath = None
            self.codepath = None
        return True

    def watchee_paths(self):
        return [w[1] for w in self.watchees]

    def show_error(self):
        print("============================")
        print(">>> Error in source file <<<")
        print("============================")
        stack = traceback.format_exc()
        print(stack)
        r = Rect(1200, 300)
        render = renderable(r)
        res = DATPenSet([
            DATPen().rect(r).f(coldtype.Gradient.V(r,
            coldtype.hsl(_random.random(), l=0.3),
            coldtype.hsl(_random.random(), l=0.3))),
        ])
        render.show_error = stack.split("\n")[-2]
        self.previews_waiting_to_paint.append([render, res, None])
    
    def show_message(self, message, scale=1):
        print(message)
    
    def apply_syntax_mods(self, source_code):
        if self.disable_syntax_mods:
            return source_code
        source_code = re.sub(r"\-\.[A-Za-z_]+([A-Za-z_0-9]+)?\(", ".noop(", source_code)
        return source_code

    def reload(self, trigger):
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
            
            elif self.filepath.suffix == ".md":
                try:
                    import exdown
                except ImportError:
                    raise Exception("pip install exdown")
                blocks = [c[0] for c in exdown.extract(str(self.filepath), syntax_filter="python")]
                source_code = "\n".join(blocks)
                if self.codepath:
                    self.codepath.unlink()
                with tempfile.NamedTemporaryFile("w", prefix="coldtype_md_src", suffix=".py", delete=False) as tf:
                    tf.write(self.apply_syntax_mods(source_code))
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
                    "__CONTEXT__": self.context,
                    "__FILE__": self.filepath,
                    "__sibling__": partial(sibling, self.filepath)
                })
                for k, v in self.program.items():
                    if isinstance(v, animation):
                        self.last_animation = v
                    
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
    
    def renderables(self, trigger):
        _rs = []
        for k, v in self.program.items():
            if isinstance(v, renderable) and not v.hidden:
                if v not in _rs:
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
            if len(matches) > 0:
                return matches

        if len(_rs) == 0:
            r = renderable((500, 500))
            def draw(r):
                #ct = coldtype.StyledString("CT", coldtype.Style("assets/ColdtypeObviously-VF.ttf", 500, wdth=0)).pen().round(1)
                #print(ct.value)
                ct = DATPen().vl([('moveTo', [(70.0, 236.0)]), ('qCurveTo', [(76.5, 236.0), (83.0, 237.5), (86.0, 238.0)]), ('qCurveTo', [(80.5, 214.0), (66.0, 153.5), (50.0, 89.0), (35.5, 28.0), (30.0, 3.5)]), ('qCurveTo', [(27.5, 2.5), (20.5, -0.5), (13.0, -2.0), (8.5, -2.0)]), ('qCurveTo', [(-2.0, -2.0), (-15.5, 6.0), (-20.0, 29.5), (-14.5, 74.5), (1.5, 148.5), (15.5, 203.5)]), ('qCurveTo', [(29.5, 259.0), (49.5, 328.0), (67.0, 364.0), (85.5, 377.0), (97.5, 377.0)]), ('qCurveTo', [(106.0, 377.0), (118.0, 374.5), (121.5, 372.0)]), ('qCurveTo', [(116.0, 352.0), (108.0, 323.0), (101.5, 297.5), (94.0, 268.5), (88.5, 247.5)]), ('qCurveTo', [(85.0, 248.5), (75.5, 250.0), (70.5, 250.0)]), ('qCurveTo', [(66.5, 250.0), (60.5, 247.5), (59.5, 244.0)]), ('qCurveTo', [(59.0, 240.0), (64.5, 236.0), (70.0, 236.0)]), ('closePath', []), ('moveTo', [(119.5, 289.5)]), ('lineTo', [(168.0, 289.5)]), ('qCurveTo', [(156.5, 242.5), (133.0, 148.5), (113.5, 67.5), (99.0, 10.5), (96.5, 0.0)]), ('qCurveTo', [(91.5, 0.5), (77.0, 1.0), (71.5, 1.0)]), ('qCurveTo', [(65.5, 1.0), (51.5, 0.5), (46.0, 0.0)]), ('qCurveTo', [(49.0, 10.5), (64.0, 67.5), (84.5, 148.5), (108.0, 242.5), (119.5, 289.5)]), ('closePath', []), ('moveTo', [(127.5, 375.0)]), ('lineTo', [(202.0, 375.0)]), ('qCurveTo', [(200.0, 365.5), (193.0, 337.5), (189.0, 323.5)]), ('qCurveTo', [(186.0, 310.5), (178.5, 281.0), (176.0, 270.0)]), ('qCurveTo', [(166.0, 270.0), (147.0, 270.5), (139.0, 270.5)]), ('qCurveTo', [(131.5, 270.5), (112.0, 270.0), (101.5, 270.0)]), ('qCurveTo', [(104.5, 281.0), (112.0, 310.5), (115.0, 323.5)]), ('qCurveTo', [(119.0, 337.5), (125.5, 365.5), (127.5, 375.0)]), ('closePath', [])])
                return DATPenSet([
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

        fmt = self.args.format or render.fmt
        _layers = self.layers if len(self.layers) > 0 else render.layers
        
        rps = []
        for rp in render.passes(trigger, _layers, self.state, indices):
            output_path = output_folder / f"{prefix}{rp.suffix}.{fmt}"

            if rp.single_layer and rp.single_layer != "__default__":
                output_path = output_folder / f"layer_{rp.single_layer}/{prefix}{rp.single_layer}_{rp.suffix}.{fmt}"

            rp.output_path = output_path
            rp.action = trigger
            rps.append(rp)
        
        return output_folder, prefix, fmt, _layers, rps

    
    def _single_thread_render(self, trigger, indices=[]) -> Tuple[int, int]:
        if not self.args.is_subprocess:
            start = ptime.time()

        renders = self.renderables(trigger)
        self.last_renders = renders
        preview_count = 0
        render_count = 0
        output_folder = None
        try:
            for render in renders:
                for watch in render.watch:
                    if isinstance(watch, coldtype.text.reader.Font) and not watch.cacheable:
                        if watch.path not in self.watchee_paths():
                            self.watchees.append([Watchable.Font, watch.path])
                        for ext in watch.font.getExternalFiles():
                            if ext not in self.watchee_paths():
                                self.watchees.append([Watchable.Font, ext])
                    elif watch not in self.watchee_paths():
                        self.watchees.append([Watchable.Generic, watch])
                
                did_render = False
                output_folder, prefix, fmt, _layers, passes = self.add_paths_to_passes(trigger, render, indices)
                render.last_passes = passes

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
                            result = render.run(rp, self.state)
                        if self.state.request:
                            self.requests_waiting.append([render, str(self.state.request)])
                            self.state.request = None
                        if not result:
                            print(">>> No result")
                            result = DATPen().rect(render.rect).f(None)

                        if previewing:
                            if render.direct_draw:
                                self.previews_waiting_to_paint.append([render, None, rp])
                            else:
                                preview_result = render.runpost(result, rp)
                                preview_count += 1
                                if preview_result:
                                    self.previews_waiting_to_paint.append([render, preview_result, rp])
                        
                        if rendering:
                            did_render = True
                            if len(render.layers) > 0 and not rp.single_layer:
                                for layer in render.layers:
                                    for layer_result in result:
                                        layer_tag = layer_result.getTag()
                                        if layer == layer_tag:
                                            if layer_tag != "__default__":
                                                layer_folder = render.layer_folder(self.filepath, layer)
                                                output_path = output_folder / layer_folder / f"{prefix}{layer}_{rp.suffix}.{fmt}"
                                            else:
                                                output_path = rp.output_path
                                            output_path.parent.mkdir(exist_ok=True, parents=True)
                                            render_count += 1
                                            self.rasterize(layer_result, render, output_path)
                                            print(">>> saved layer...", str(output_path.relative_to(Path.cwd())))
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
                "-l", ",".join(self.layers or []),
                "-s", str(self.args.scale),
            ]
            r = self.args.rasterizer
            if r:
                sargs.append("-r", r)
            if self.args.no_sound:
                sargs.append("-ns")
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
            if render.fmt == "png":
                SkiaPen.Composite(content, render.rect, str(path), scale=scale, context=None if self.args.cpu_render else self.context)
            elif render.fmt == "pdf":
                SkiaPen.PDFOnePage(content, render.rect, str(path), scale=scale)
            else:
                print("> Skia render not supported for ", render.fmt)
        elif rasterizer == "svg":
            from coldtype.pens.svgpen import SVGPen
            path.write_text(SVGPen.Composite(content, render.rect, viewBox=render.viewBox))
        elif rasterizer == "cairo":
            from coldtype.pens.cairopen import CairoPen
            CairoPen.Composite(content, render.rect, str(path), scale=scale)
        elif rasterizer == "pickle":
            pickle.dump(content, open(path, "wb"))
        else:
            raise Exception(f"rasterizer ({rasterizer}) not supported")
    
    def reload_and_render(self, trigger, watchable=None, indices=None):
        if self.args.is_subprocess:
            if not glfw.init():
                raise RuntimeError('glfw.init() failed')
            glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
            glfw.window_hint(glfw.STENCIL_BITS, 8)
            window = glfw.create_window(640, 480, '', None, None)
            glfw.make_context_current(window)
            self.context = skia.GrDirectContext.MakeGL()

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
    
    def initialize_gui_and_server(self):
        try:
            self.server = echo_server()
            self.server_thread = WebSocketThread(self.server)
            self.server_thread.start()
        except OSError:
            self.server = None

        if not glfw.init():
            raise RuntimeError('glfw.init() failed')
        glfw.window_hint(glfw.STENCIL_BITS, 8)

        if self.py_config.get("WINDOW_BACKGROUND"):
            glfw.window_hint(glfw.FOCUSED, glfw.FALSE)
        if self.py_config.get("WINDOW_FLOAT"):
            glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        
        self.window = glfw.create_window(int(50), int(50), '', None, None)
        self.window_scrolly = 0

        recp = sibling(__file__, "../../assets/RecMono-CasualItalic.ttf")
        self.typeface = skia.Typeface.MakeFromFile(str(recp))
        #print(self.typeface.serialize().bytes().decode("utf-8"))
        
        o = self.py_config.get("WINDOW_OPACITY")
        if o:
            glfw.set_window_opacity(self.window, max(0.1, min(1, o)))
        
        self._prev_scale = glfw.get_window_content_scale(self.window)[0]
        
        glfw.make_context_current(self.window)
        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_char_callback(self.window, self.on_character)
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(self.window, self.on_mouse_move)
        glfw.set_scroll_callback(self.window, self.on_scroll)

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
                    print(f">>> no midi port found with that name ({device}) <<<")
        except:
            self.midis = []
        
        self.context = skia.GrDirectContext.MakeGL()

        #self.watch_file_changes()

        if len(self.watchees) > 0:
            glfw.set_window_title(self.window, self.watchees[0][1].name)
        else:
            glfw.set_window_title(self.window, "coldtype")

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
            if not self.args.watch:
                should_halt = True
            else:
                should_halt = self.before_start()
        else:
            should_halt = self.before_start()
        
        if self.args.watch:
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
            if self.args.watch:
                self.listen_to_glfw()
            else:
                self.on_exit()
    
    def before_start(self):
        pass

    def on_start(self):
        pass

    def on_request_from_render(self, render, request):
        print("request (noop)>", render, request)

    def on_hotkey(self, key_combo, action):
        print("HOTKEY", key_combo)
        self.action_waiting = action
    
    def on_message(self, message, action):
        if action:
            enum_action = self.lookup_action(action)
            if enum_action:
                print("ENUM_ACTION", enum_action)
                self.on_action(enum_action, message)
            else:
                print(">>> (", action, ") is not a recognized action")

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
                    output_folder, prefix, fmt, _layers, passes = self.add_paths_to_passes(trigger, render, [0])
                    for rp in passes:
                        all_passes.append(rp)

            release_fn(all_passes)
        except Exception as e:
            print("Release failed", str(e))
    
    def on_mouse_button(self, _, btn, action, mods):
        if self.state.keylayer != 0:
            pos = Point(glfw.get_cursor_pos(self.window)).scale(2) # TODO should this be preview-scale?
            pos[1] = self.last_rect.h - pos[1]
            requested_action = self.state.on_mouse_button(pos, btn, action, mods)
            if requested_action:
                self.action_waiting = requested_action
    
    def on_mouse_move(self, _, xpos, ypos):
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

    def on_key(self, win, key, scan, action, mods):
        if self.state.keylayer != Keylayer.Default:
            requested_action = self.state.on_key(win, key, scan, action, mods)
            if requested_action:
                self.action_waiting = requested_action
            return
        
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_LEFT:
                self.action_waiting = Action.PreviewStoryboardPrev
            elif key == glfw.KEY_RIGHT:
                self.action_waiting = Action.PreviewStoryboardNext
            elif key == glfw.KEY_HOME:
                self.state.frame_index_offset = 0
                self.action_waiting = Action.PreviewStoryboard

        if action != glfw.PRESS:
            return
        
        if key == glfw.KEY_DOWN:
            if mods & glfw.MOD_SUPER:
                o = glfw.get_window_opacity(self.window)
                glfw.set_window_opacity(self.window, max(0.1, o-0.1))
            else:
                self.window_scrolly -= (500 if mods & glfw.MOD_SHIFT else 250)
                self.on_action(Action.PreviewStoryboard)
        elif key == glfw.KEY_UP:
            if mods & glfw.MOD_SUPER:
                o = glfw.get_window_opacity(self.window)
                glfw.set_window_opacity(self.window, min(1, o+0.1))
            else:
                self.window_scrolly += (500 if mods & glfw.MOD_SHIFT else 250)
                self.on_action(Action.PreviewStoryboard)
        elif key == glfw.KEY_SPACE:
            #if mods & glfw.MOD_CONTROL:
            self.on_action(Action.RenderedPlay)
            #else:
            #    self.on_action(Action.PreviewPlay)
        elif key == glfw.KEY_ENTER:
            self.on_action(Action.PreviewStoryboardReload)
        elif key in [glfw.KEY_MINUS, glfw.KEY_EQUAL]:
            inc = -0.1 if key == glfw.KEY_MINUS else 0.1
            if mods & glfw.MOD_SHIFT:
                inc = inc * 5
            self.state.preview_scale = max(0.1, min(5, self.state.preview_scale + inc))
            self._should_reload = True
        elif key == glfw.KEY_0:
            self.state.preview_scale = 1.0
            self._should_reload = True
        elif key == glfw.KEY_R:
            self.on_action(Action.RestartRenderer)
        elif key == glfw.KEY_L:
            self.on_action(Action.Release)
        elif key == glfw.KEY_P:
            #self._should_reload = True
            self.on_action(Action.PreviewStoryboardReload)
        elif key == glfw.KEY_A:
            self.on_action(Action.RenderAll)
        elif key == glfw.KEY_W:
            self.on_action(Action.RenderWorkarea)
        elif key == glfw.KEY_M:
            self.on_action(Action.ToggleMultiplex)
        elif key == glfw.KEY_D:
            self.state.keylayer = Keylayer.Editing
            self.state.keylayer_shifting = True
            #self.on_action(Action.PreviewStoryboard) # only necessary if not a charpoint
        elif key == glfw.KEY_C:
            self.state.keylayer = Keylayer.Cmd
            self.state.keylayer_shifting = True
        elif key == glfw.KEY_Q:
            self.dead = True
            self.on_exit()
    
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
            self.on_action(Action.Release)
        elif action_abbrev == "m":
            self.on_action(Action.ToggleMultiplex)
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
        action, data = self.stdin_to_action(stdin)
        if action:
            if action == Action.PreviewIndices:
                self.render(action, indices=data)
            elif action == Action.RestartRenderer:
                self.on_exit(restart=True)
            else:
                self.on_action(action)

    def on_action(self, action, message=None) -> bool:
        if action in [Action.RenderAll, Action.RenderWorkarea, Action.PreviewStoryboardReload]:
            self.reload_and_render(action)
            return True
        elif action in [Action.PreviewStoryboard]:
            self.render(Action.PreviewStoryboard)
        elif action in [Action.PreviewStoryboardNext, Action.PreviewStoryboardPrev, Action.PreviewPlay]:
            if action == Action.PreviewPlay:
                if self.playing == 0:
                    self.playing = 1
                else:
                    self.playing = 0
            if action == Action.PreviewStoryboardPrev:
                self.state.frame_index_offset -= 1
            elif action == Action.PreviewStoryboardNext:
                self.state.frame_index_offset += 1
            self.render(Action.PreviewStoryboard)
        elif action == Action.RenderedPlay:
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
        elif action == Action.SaveControllers:
            self.state.persist()
        elif action == Action.ClearControllers:
            self.state.clear()
            self.on_action(Action.PreviewStoryboard)
        elif action == Action.ResetControllers:
            self.state.reset()
            self.on_action(Action.PreviewStoryboard)
        elif action == Action.RestartRenderer:
            self.on_exit(restart=True)
        elif action == Action.Kill:
            os.kill(os.getpid(), signal.SIGINT)
            #self.on_exit(restart=False)
        elif action == Action.ToggleMultiplex:
            self.multiplexing = not self.multiplexing
            print(">>> MULTIPLEXING?", self.multiplexing)
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
        animation = self.animation()
        if animation and animation.timeline:
            print("EVENT", action, kwargs)
            if action:
                kwargs["action"] = action.value
            kwargs["prefix"] = self.filepath.stem
            kwargs["fps"] = animation.timeline.fps
            if self.server:
                for k, client in self.server.connections.items():
                    client.sendMessage(json.dumps(kwargs))
            else:
                print("Animation server must be primary")
    
    def process_ws_message(self, message):
        try:
            jdata = json.loads(message)
            action = jdata.get("action")
            if action:
                self.on_message(jdata, jdata.get("action"))
            elif jdata.get("metadata") and jdata.get("path"):
                path = Path(jdata.get("path"))
                if self.args.monitor_lines and path == self.filepath:
                    self.line_number = jdata.get("line_number")
        except TypeError:
            raise TypeError("Huh")
        except:
            self.show_error()
            print("Malformed message", message)
    
    def listen_to_glfw(self):
        while not self.dead and not glfw.window_should_close(self.window):
            scale_x, scale_y = glfw.get_window_content_scale(self.window)
            if scale_x != self._prev_scale:
                self._prev_scale = scale_x
                self.on_action(Action.PreviewStoryboard)
            
            if self._should_reload:
                self._should_reload = False
                self.on_action(Action.PreviewStoryboard)
            
            t = glfw.get_time()
            td = t - self.glfw_last_time

            if self.last_animation and self.playing_preloaded_frame >= 0 and len(self.preloaded_frames) > 0:
                spf = 1 / float(self.last_animation.timeline.fps)
                if td >= spf:
                    self.glfw_last_time = t
                else:
                    glfw.poll_events()
                    continue

                GL.glClear(GL.GL_COLOR_BUFFER_BIT)

                with self.surface as canvas:
                    path = self.preloaded_frames[self.playing_preloaded_frame]
                    c = self.last_animation.bg
                    canvas.clear(c.skia())
                    image = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(path)))
                    canvas.drawImage(image, 0, 0)
                
                self.surface.flushAndSubmit()
                glfw.swap_buffers(self.window)

                self.playing_preloaded_frame += 1
                if self.playing_preloaded_frame == len(self.preloaded_frames):
                    self.playing_preloaded_frame = 0
                ptime.sleep(0.01)
            else:
                ptime.sleep(0.01)
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
                
                if self.playing != 0:
                    self.on_action(Action.PreviewStoryboardNext)
            
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
    
    def turn_over(self):
        if self.action_waiting:
            #print(">", self.action_waiting)
            #self.on_message({}, self.action_waiting)
            self.on_action(self.action_waiting)
            self.action_waiting = None
        
        if self.server:
            for k, v in self.server.connections.items():
                if hasattr(v, "messages") and len(v.messages) > 0:
                    #print(k, v.messages)
                    for msg in v.messages:
                        self.process_ws_message(msg)
                    v.messages = []

        if self.server:
            self.monitor_midi()
        
        if len(self.waiting_to_render) > 0:
            for action, path in self.waiting_to_render:
                self.reload_and_render(action, path)
            self.waiting_to_render = []
        
        dscale = self.preview_scale()
        rects = []

        render_previews = len(self.previews_waiting_to_paint) > 0
        if render_previews:
            w = 0
            lh = -1
            h = 0
            for render, result, rp in self.previews_waiting_to_paint:
                if hasattr(render, "show_error"):
                    sr = render.rect
                else:
                    sr = render.rect.scale(dscale, "mnx", "mny").round()
                w = max(sr.w, w)
                rects.append(Rect(0, lh+1, sr.w, sr.h))
                lh += sr.h + 1
                h += sr.h + 1
            h -= 1
            
            frect = Rect(0, 0, w, h)
            if frect != self.last_rect:
                self.create_surface(frect)

            if not self.last_rect or frect != self.last_rect:
                m_scale = self.py_config.get("WINDOW_SCALE")
                if m_scale:
                    scale_x, scale_y = m_scale
                else:
                    scale_x, scale_y = glfw.get_window_content_scale(self.window)
                
                if not DARWIN:
                    scale_x, scale_y = 1.0, 1.0

                ww = int(w/scale_x)
                wh = int(h/scale_y)
                glfw.set_window_size(self.window, ww, wh)
                pin = self.py_config.get("WINDOW_PIN", None)
                if pin:
                    monitor = glfw.get_primary_monitor()
                    work_rect = Rect(glfw.get_monitor_workarea(monitor))
                    pinned = work_rect.take(ww, pin[0]).take(wh, pin[1])
                    glfw.set_window_pos(self.window, pinned.x, pinned.y)

            self.last_rect = frect

            GL.glClear(GL.GL_COLOR_BUFFER_BIT)

            with self.surface as canvas:
                canvas.clear(skia.Color4f(0.3, 0.3, 0.3, 1))

                for idx, (render, result, rp) in enumerate(self.previews_waiting_to_paint):
                    rect = rects[idx].offset((w-rects[idx].w)/2, 0).round()
                    self.draw_preview(dscale, canvas, rect, (render, result, rp))
            
                if self.state.keylayer != Keylayer.Default:
                    self.state.draw_keylayer(canvas, self.last_rect, self.typeface)
            
            self.surface.flushAndSubmit()
            glfw.swap_buffers(self.window)
        
        self.state.needs_display = 0
        self.previews_waiting_to_paint = []
    
        for render, request in self.requests_waiting:
            self.on_request_from_render(render, request)
            self.requests_waiting = []

    def draw_preview(self, scale, canvas, rect, waiter):
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
        canvas.drawRect(skia.Rect(0, 0, rect.w, rect.h), skia.Paint(Color=render.bg.skia()))
        if not hasattr(render, "show_error"):
            canvas.scale(scale, scale)
        if render.clip:
            canvas.clipRect(skia.Rect(0, 0, rect.w, rect.h))
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
            render.draw_preview(1.0, canvas, render.rect, result, rp)
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
        if path in self.watchee_paths():
            if path.suffix == ".json":
                try:
                    json.loads(path.read_text())
                except json.JSONDecodeError:
                    print("Error decoding watched json", path)
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
            print(f">>> resave: {Path(event.src_path).relative_to(Path.cwd())}")
            
            if self.args.memory and process:
                memory = bytesto(process.memory_info().rss)
                diff = memory - self._last_memory
                self._last_memory = memory
                print(">>> pid:{:d}/new:{:04.2f}MB/total:{:4.2f}".format(os.getpid(), diff, memory))
            
            self.waiting_to_render = [[Action.Resave, self.watchees[idx][0]]]

    def watch_file_changes(self):
        self.observers = []
        dirs = set([w[1].parent for w in self.watchees])
        for d in dirs:
            o = AsyncWatchdog(str(d), on_modified=self.on_modified, recursive=False)
            o.start()
            self.observers.append(o)
        if self.filepath:
            print(f"... watching {self.filepath.name} for changes ...")
        else:
            print(f"... no file specified, showing generic window ...")
    
    def monitor_midi(self):
        controllers = {}
        for device, mi in self.midis:
            msg = mi.getMessage(0)
            while msg:
                if self.args.midi_info:
                    print(device, msg)
                if msg.isNoteOn(): # Maybe not forever?
                    nn = msg.getNoteNumber()
                    action = self.midi_mapping[device]["note_on"].get(nn)
                    if action:
                        self.on_message({}, action)
                if msg.isController():
                    controllers[device + "_" + str(msg.getControllerNumber())] = msg.getControllerValue()/127
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

            self.on_action(Action.PreviewStoryboard, {})
    
    def stop_watching_file_changes(self):
        for o in self.observers:
            o.stop()
        
    def reset_renderers(self):
        for r in self.running_renderers:
            if r:
                r.terminate()

    def on_exit(self, restart=False):
        #if self.args.watch:
        #   print(f"<EXIT(restart:{restart})>")
        glfw.terminate()
        if self.context:
            self.context.abandonContext()
        if self.hotkeys:
            self.hotkeys.stop()
        self.reset_renderers()
        self.stop_watching_file_changes()
        if self.server_thread:
            self.server_thread.should_run = False
        if self.args.memory:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('traceback')

            # pick the biggest memory block
            stat = top_stats[0]
            print("%s memory blocks: %.1f KiB" % (stat.count, stat.size / 1024))
            for line in stat.traceback.format():
                print(line)
        
        if restart:
            print(">>>>>>>>>>>>>>> RESTARTING <<<<<<<<<<<<<<<")
            os.execl(sys.executable, *(["-m"]+sys.argv))


def main():
    pargs, parser = Renderer.Argparser()
    Renderer(parser).main()

if __name__ == "__main__":
    main()