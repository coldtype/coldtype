import sys, os, re, signal, tracemalloc
import tempfile, traceback, threading
import argparse, importlib, inspect, json, math
import platform

import time as ptime
from pathlib import Path
from typing import Tuple
from random import shuffle, Random
from runpy import run_path
from subprocess import call, Popen
from functools import partial

import skia, coldtype
from coldtype.helpers import *
from coldtype.geometry import Rect
from coldtype.pens.skiapen import SkiaPen
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.renderable import renderable, Action, animation
from coldtype.renderer.watchdog import AsyncWatchdog
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

# https://stackoverflow.com/questions/27174736/how-to-read-most-recent-line-from-stdin-in-python
last_line = ''
new_line_event = threading.Event()

def keep_last_line():
    global last_line, new_line_event
    for line in sys.stdin:
        last_line = line
        new_line_event.set()

keep_last_line_thread = threading.Thread(target=keep_last_line)
keep_last_line_thread.daemon = True
keep_last_line_thread.start()


class Renderer():
    def Argparser(name="coldtype", file=True, nargs=[]):
        parser = argparse.ArgumentParser(prog=name, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        
        if file:
            parser.add_argument("file", type=str, nargs="?", help="The source file for a coldtype render")
        for narg in nargs:
            parser.add_argument(narg[0], nargs="?", default=narg[1])
        
        pargs = dict(
            version=parser.add_argument("-v", "--version", action="store_true", default=False, help="Display version"),

            watch=parser.add_argument("-w", "--watch", action="store_true", default=True, help="Watch for changes to source files"),
            
            save_renders=parser.add_argument("-sv", "--save-renders", action="store_true", default=False, help="Should the renderer create image artifacts?"),
            
            rasterizer=parser.add_argument("-r", "--rasterizer", type=str, default="skia", choices=["drawbot", "cairo", "svg", "skia"], help="Which rasterization engine should coldtype use to create artifacts?"),

            raster_previews=parser.add_argument("-rp", "--raster-previews", action="store_true", default=False, help="Should rasters be displayed in the Coldtype viewer?"),
            
            scale=parser.add_argument("-s", "--scale", type=float, default=1.0, help="When save-renders is engaged, what scale should images be rasterized at? (Useful for up-rezing)"),

            preview_scale=parser.add_argument("-ps", "--preview-scale", type=float, default=1.0, help="What size should previews be shown at?"),
            
            all=parser.add_argument("-a", "--all", action="store_true", default=False, help="If rendering an animation, pass the -a flag to render all frames sequentially"),

            multiplex=parser.add_argument("-mp", "--multiplex", action="store_true", default=False, help="Render in multiple processes"),

            memory=parser.add_argument("-m", "--memory", action="store_true", default=False, help="Show statistics about memory usage?"),

            midi_info=parser.add_argument("-mi", "--midi-info", action="store_true", default=False, help="Show available MIDI devices"),

            is_subprocess=parser.add_argument("-isp", "--is-subprocess", action="store_true", default=False, help=argparse.SUPPRESS),

            thread_count=parser.add_argument("-tc", "--thread-count", type=int, default=8, help="How many threads when multiplexing?"),

            no_sound=parser.add_argument("-ns", "--no-sound", action="store_true", default=False, help="Don’t make sound"),
            
            format=parser.add_argument("-fmt", "--format", type=str, default=None, help="What image format should be saved to disk?"),

            layers=parser.add_argument("-l", "--layers", type=str, default=None, help="comma-separated list of layers to flag as renderable (if None, will flag all layers as renderable)"),

            indices=parser.add_argument("-i", "--indices", type=str, default=None),

            file_prefix=parser.add_argument("-fp", "--file-prefix", type=str, default="", help="Should the output files be prefixed with something? If so, put it here."),

            output_folder=parser.add_argument("-of", "--output-folder", type=str, default=None, help="If you don’t want to render to the default output location, specify that here."),

            monitor_lines=parser.add_argument("-ml", "--monitor-lines", action="store_true", default=False, help=argparse.SUPPRESS),

            filter_functions=parser.add_argument("-ff", "--filter-functions", type=str, default=None, help="Names of functions to render"),

            show_exit_code=parser.add_argument("-sec", "--show-exit-code", action="store_true", default=False, help=argparse.SUPPRESS),

            show_render_count=parser.add_argument("-src", "--show-render-count", action="store_true", default=False, help=argparse.SUPPRESS)),
        return pargs, parser

    def __init__(self, parser, no_socket_ok=False):
        try:
            py_config = run_path(str(Path("~/coldtype.py").expanduser()))
            self.py_config = py_config
            self.midi_mapping = py_config.get("MIDI", {})
            self.hotkey_mapping = py_config.get("HOTKEYS", {})
        except FileNotFoundError:
            print(">>> no coldtype config found <<<")
            self.py_config = {}
            self.midi_mapping = {}
            self.hotkey_mapping = None
        except json.decoder.JSONDecodeError:
            print(">>> syntax error in ~/coldtype.json <<<")
            sys.exit(0)

        sys.path.insert(0, os.getcwd())

        self.args = parser.parse_args()
        if self.args.is_subprocess or self.args.all:
            self.args.watch = False

        self.watchees = []
        self.reset_filepath(self.args.file if hasattr(self.args, "file") else None)
        self.layers = [l.strip() for l in self.args.layers.split(",")] if self.args.layers else []
        
        if self.args.watch:
            self.server = echo_server()
        else:
            self.server = None

        self.program = None
        self.websocket = None
        self.exit_code = 0

        self.line_number = -1
        self.last_renders = []

        self.controller_values = {}

        # for multiplex mode
        self.running_renderers = []
        self.completed_renderers = []

        self.observers = []
        self.action_waiting = None
        self.waiting_to_render = []
        self.previews_waiting_to_paint = []
        self.preloaded_frames = []
        self.playing_preloaded_frame = -1
        self.glfw_last_time = -1
        self.last_animation = None
        self.playing = 0
        self.hotkeys = None
        self.context = None
        self.surface = None
        self._preview_scale = self.args.preview_scale
        self._should_reload = False

        if self.args.watch:
            if not glfw.init():
                raise RuntimeError('glfw.init() failed')
            glfw.window_hint(glfw.STENCIL_BITS, 8)

            if self.py_config.get("WINDOW_BACKGROUND"):
                glfw.window_hint(glfw.FOCUSED, glfw.FALSE)
            if self.py_config.get("WINDOW_FLOAT"):
                glfw.window_hint(glfw.FLOATING, glfw.TRUE)
            
            self.window = glfw.create_window(int(50), int(50), '', None, None)

            if o := self.py_config.get("WINDOW_OPACITY"):
                glfw.set_window_opacity(self.window, max(0.1, min(1, o)))
            
            self._prev_scale = glfw.get_window_content_scale(self.window)[0]
            
            glfw.make_context_current(self.window)
            glfw.set_key_callback(self.window, self.on_key)
    
    def reset_filepath(self, filepath):
        self.line_number = -1
        if filepath:
            self.filepath = Path(filepath).expanduser().resolve()
            self.watchees = [[Watchable.Source, self.filepath]]
        else:
            self.filepath = None

    def watchee_paths(self):
        return [w[1] for w in self.watchees]

    def show_error(self):
        print(">>> CAUGHT COLDTYPE RENDER")
        print(traceback.format_exc())
    
    def show_message(self, message, scale=1):
        print(message)

    def reload(self, trigger):
        if not self.filepath:
            self.program = dict(no_filepath=True)
            pass # ?
        else:
            try:
                self.program = run_path(str(self.filepath), init_globals={"CMC": self.controller_values})
                for k, v in self.program.items():
                    if isinstance(v, coldtype.text.reader.Font):
                        v.load()
                        if v.path not in self.watchee_paths():
                            self.watchees.append([Watchable.Font, v.path])
                        for ext in v.font.getExternalFiles():
                            if ext not in self.watchee_paths():
                                self.watchees.append([Watchable.Font, ext])
                    elif isinstance(v, DefconFont):
                        p = Path(v.path).resolve()
                        if p not in self.watchee_paths():
                            self.watchees.append([Watchable.Font, p])
                    elif isinstance(v, animation):
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
    
    def renderables(self, trigger):
        _rs = []
        for k, v in self.program.items():
            if isinstance(v, renderable) and not v.hidden:
                _rs.append(v)
        if self.args.filter_functions:
            function_names = [f.strip() for f in self.args.filter_functions.split(",")]
            _rs = [r for r in _rs if r.func.__name__ in function_names]
        if self.args.monitor_lines and trigger != Action.RenderAll:
            func_name = file_and_line_to_def(self.filepath, self.line_number)
            matches = [r for r in _rs if r.func.__name__ == func_name]
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
        prefix = self.args.file_prefix or render.prefix or self.filepath.stem if self.filepath else None
        fmt = self.args.format or render.fmt
        _layers = self.layers if len(self.layers) > 0 else render.layers
        
        rps = []
        for rp in render.passes(trigger, _layers, indices):
            output_path = output_folder / f"{prefix}_{rp.suffix}.{fmt}"

            if rp.single_layer and rp.single_layer != "__default__":
                output_path = output_folder / f"layer_{rp.single_layer}/{prefix}_{rp.single_layer}_{rp.suffix}.{fmt}"

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
        try:
            for render in renders:
                for watch in render.watch:
                    if watch not in self.watchee_paths():
                        self.watchees.append([Watchable.Font, watch])
                
                did_render = False
                output_folder, prefix, fmt, _layers, passes = self.add_paths_to_passes(trigger, render, indices)

                previewing = (trigger in [
                    Action.Initial,
                    Action.Resave,
                    Action.PreviewStoryboard,
                    Action.PreviewIndices,
                ])
                
                rendering = (self.args.save_renders or trigger in [
                    Action.RenderAll,
                    Action.RenderWorkarea,
                    Action.RenderIndices,
                ])
                
                for rp in passes:
                    output_path = rp.output_path

                    try:
                        result = render.run(rp)
                        try:
                            if len(result) == 2 and isinstance(result[1], str):
                                self.show_message(result[1])
                                result = result[0]
                        except:
                            pass
                        if previewing:
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
                                                output_path = output_folder / layer_folder / f"{prefix}_{layer}_{rp.suffix}.{fmt}"
                                            else:
                                                output_path = rp.output_path
                                            output_path.parent.mkdir(exist_ok=True, parents=True)
                                            render_count += 1
                                            self.rasterize(layer_result, render, output_path)
                                            print(">>> saved layer...", str(output_path.relative_to(Path.cwd())))
                            else:
                                render_count += 1
                                output_path.parent.mkdir(exist_ok=True, parents=True)
                                if render.self_rasterizing:
                                    print(">>> self-rasterized...", output_path.relative_to(Path.cwd()))
                                else:
                                    self.rasterize(result or DATPen(), render, output_path)
                                    # TODO a progress bar?
                                    print(">>> saved...", str(output_path.relative_to(Path.cwd())))
                    except:
                        self.show_error()
                if did_render:
                    render.package(self.filepath, output_folder)
        except:
            self.show_error()
        if render_count > 0:
            self.show_message(f"Rendered {render_count}")
        
        if not self.args.is_subprocess:
            print("TIME >>>", ptime.time() - start)
        
        return preview_count, render_count

    def render(self, trigger, indices=[]) -> Tuple[int, int]:
        if self.args.is_subprocess: # is a child process of a multiplexed render
            if trigger != Action.RenderIndices:
                raise Exception("Invalid child process render action")
                return 0, 0
            else:
                p, r = self._single_thread_render(trigger, indices=indices)
                if not self.args.no_sound:
                    os.system("afplay /System/Library/Sounds/Pop.aiff")
                self.exit_code = 5 # mark as child-process
                return p, r
        
        elif self.args.multiplex:
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
        
        preview_count, render_count = self._single_thread_render(trigger, indices)
        
        if not self.args.is_subprocess and render_count > 0:
            self.send_to_external(None, rendered=True)

        return preview_count, render_count
    
    def render_multiplexed(self, frames):
        start = ptime.time()
        
        group = math.floor(len(frames) / self.args.thread_count)
        ordered_frames = list(range(frames[0], frames[0]+len(frames)))
        shuffle(ordered_frames)
        subslices = list(chunks(ordered_frames, group))
        
        self.reset_renderers()
        self.running_renderers = []
        self.completed_renderers = []

        #logfile = filepath.parent.joinpath(f"{filepath.stem}-log.txt")
        #log = open(logfile, "w")

        for subslice in subslices:
            print("slice >", len(subslice))
            sargs = [
                "coldtype",
                sys.argv[1],
                "-i", ",".join([str(s) for s in subslice]),
                "-r", self.args.rasterizer,
                "-isp",
                "-l", ",".join(self.layers or []),
                "-s", str(self.args.scale),
            ]
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
            SkiaPen.Composite(content, render.rect, str(path), scale=scale)
        elif rasterizer == "svg":
            from coldtype.pens.svgpen import SVGPen
            path.write_text(SVGPen.Composite(content, render.rect, viewBox=True))
        elif rasterizer == "cairo":
            from coldtype.pens.cairopen import CairoPen
            CairoPen.Composite(content, render.rect, str(path), scale=scale)
        else:
            raise Exception(f"rasterizer ({rasterizer}) not supported")
    
    def reload_and_render(self, trigger, watchable=None, indices=None):
        wl = len(self.watchees)

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
            from pprint import pprint
            pprint(self.watchees)
            self.stop_watching_file_changes()
            self.watch_file_changes()

    def main(self):
        if self.args.memory:
            tracemalloc.start(10)
            self._last_memory = -1
        try:
            #asyncio.get_event_loop().run_until_complete(self.start())
            self.start()
        except KeyboardInterrupt:
            print("INTERRUPT")
            self.on_exit()
        if self.args.show_exit_code:
            print("exit>", self.exit_code)
        sys.exit(self.exit_code)

    def start(self):
        if self.args.version:
            print(">>>", coldtype.__version__)
            should_halt = True
        elif self.args.midi_info:
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
                            print(">>> no midi port found with that name <<<")
                except:
                    self.midis = []

                self.watch_file_changes()
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

                self.listen_to_glfw()
            else:
                self.on_exit()
    
    def before_start(self):
        pass

    def on_start(self):
        pass

    def on_hotkey(self, key_combo, action):
        print("HOTKEY", key_combo)
        self.action_waiting = action
    
    def on_message(self, message, action):
        if action:
            enum_action = self.lookup_action(action)
            if enum_action:
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
    
    def on_key(self, win, key, scan, action, mods):
        if action == glfw.PRESS:
            if key == glfw.KEY_LEFT:
                self.on_action(Action.PreviewStoryboardPrev)
            elif key == glfw.KEY_RIGHT:
                self.on_action(Action.PreviewStoryboardNext)
            elif key == glfw.KEY_DOWN:
                o = glfw.get_window_opacity(self.window)
                glfw.set_window_opacity(self.window, max(0.1, o-0.1))
            elif key == glfw.KEY_UP:
                o = glfw.get_window_opacity(self.window)
                glfw.set_window_opacity(self.window, min(1, o+0.1))
            elif key == glfw.KEY_SPACE:
                if mods & glfw.MOD_CONTROL:
                    self.on_action(Action.RenderedPlay)
                else:
                    self.on_action(Action.PreviewPlay)
            elif key in [glfw.KEY_MINUS, glfw.KEY_EQUAL]:
                inc = -0.1 if key == glfw.KEY_MINUS else 0.1
                if mods & glfw.MOD_SHIFT:
                    inc = inc * 5
                self._preview_scale = max(0.1, min(5, self._preview_scale + inc))
                self._should_reload = True
            elif key == glfw.KEY_0:
                self._preview_scale = 1.0
                self._should_reload = True
            elif key == glfw.KEY_R:
                self.on_action(Action.RestartRenderer)
            elif key == glfw.KEY_P:
                self._should_reload = True
            elif key == glfw.KEY_A:
                self.on_action(Action.RenderAll)
    
    def stdin_to_action(self, stdin):
        action_abbrev, *data = stdin.split(" ")
        if action_abbrev == "ps":
            return Action.PreviewStoryboard, None
        elif action_abbrev == "n":
            return Action.PreviewStoryboardNext, None
        elif action_abbrev == "p":
            return Action.PreviewStoryboardPrev, None
        elif action_abbrev == "ra":
            return Action.RenderAll, None
        elif action_abbrev == "rw":
            return Action.RenderWorkarea, None
        elif action_abbrev == "pf":
            return Action.PreviewIndices, [int(i.strip()) for i in data]
        elif action_abbrev == "rr":
            return Action.RestartRenderer, None
        elif action_abbrev == "rp":
            self.reset_filepath(data[0])
            return Action.PreviewStoryboard, None
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
        if action in [Action.PreviewStoryboard, Action.RenderAll, Action.RenderWorkarea]:
            self.reload_and_render(action)
            return True
        elif action in [Action.PreviewStoryboardNext, Action.PreviewStoryboardPrev, Action.PreviewPlay]:
            if action == Action.PreviewPlay:
                if self.playing == 0:
                    self.playing = 1
                else:
                    self.playing = 0
            increment = -1 if action == Action.PreviewStoryboardPrev else 1
            for render in self.last_renders:
                if hasattr(render, "storyboard"):
                    for idx, fidx in enumerate(render.storyboard):
                        nidx = (fidx + increment) % render.duration
                        render.storyboard[idx] = nidx
                    self.render(Action.PreviewStoryboard)
            return True
        elif action == Action.RenderedPlay:
            if self.playing_preloaded_frame >= 0:
                self.playing_preloaded_frame = -1
                self.preloaded_frames = []
            else:
                anm = self.animation()
                passes = self.add_paths_to_passes(Action.RenderAll, anm, anm.all_frames())[-1]
                self.preload_frames(passes)
        elif action == Action.ArbitraryCommand:
            self.on_stdin(message.get("input"))
            return True
        elif action == Action.UICallback:
            for render in self.renderables(action):
                if render.ui_callback:
                    render.ui_callback(message)
        elif action == Action.RestartRenderer:
            self.on_exit(restart=True)
        elif action == Action.Kill:
            os.kill(os.getpid(), signal.SIGINT)
            #self.on_exit(restart=False)
        elif message.get("serialization"):
            ptime.sleep(1)
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
            for client in echo_clients:
                client.sendMessage(json.dumps(kwargs))
    
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
        while not glfw.window_should_close(self.window):
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
                #if td < (1/float(self.last_animation.timeline.fps)):
                #    glfw.poll_events()
                #    continue
                ptime.sleep(0.01)
                GL.glClear(GL.GL_COLOR_BUFFER_BIT)

                #print(td)
                w = self.last_animation.rect.w
                h = self.last_animation.rect.h
                #print(w, h, self.last_animation.timeline.fps)
                if not self.context:
                    self.context = skia.GrDirectContext.MakeGL()
                    backend_render_target = skia.GrBackendRenderTarget(
                        int(w), int(h), 0, 0,
                        skia.GrGLFramebufferInfo(0, GL.GL_RGBA8))
                    self.surface = skia.Surface.MakeFromBackendRenderTarget(
                        context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
                        skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
                
                assert self.surface is not None

                with self.surface as canvas:
                    path = self.preloaded_frames[self.playing_preloaded_frame]
                    c = coldtype.hsl(_random.random())
                    c = self.last_animation.bg
                    canvas.drawRect(skia.Rect(0, 0, w, h), skia.Paint(Color=c.skia()))
                    image = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(path)))
                    #image = skia.Image.open(str(path))
                    canvas.drawImage(image, 0, 0)
                    #image.unref()
                
                surface.flushAndSubmit()
                glfw.swap_buffers(self.window)

                self.playing_preloaded_frame += 1
                if self.playing_preloaded_frame == len(self.preloaded_frames):
                    self.playing_preloaded_frame = 0
            else:
                self.glfw_last_time = t
                #ptime.sleep(0.5)
                self.turn_over()
                global last_line
                if last_line:
                    self.on_stdin(last_line.strip())
                    last_line = None
                
                if self.playing != 0:
                    self.on_action(Action.PreviewStoryboardNext)
            
            glfw.poll_events()
        self.on_exit(restart=False)
    
    def preview_scale(self):
        return self._preview_scale
    
    def turn_over(self):
        if self.action_waiting:
            self.on_message({}, self.action_waiting)
            self.action_waiting = None
        
        global echo_incoming
        if len(echo_incoming) > 0:
            for echo, msg in echo_incoming:
                print("WS>>>", echo.address, msg)
                self.process_ws_message(msg)
            echo_incoming = []

        self.monitor_midi()
        if len(self.waiting_to_render) > 0:
            for action, path in self.waiting_to_render:
                self.reload_and_render(action, path)
            self.waiting_to_render = []
        
        dscale = self.preview_scale()
        rects = []

        if len(self.previews_waiting_to_paint) > 0:
            w = 0
            lh = -1
            h = 0
            for render, result, rp in self.previews_waiting_to_paint:
                sr = render.rect.scale(dscale, "mnx", "mny").round()
                w = max(sr.w, w)
                rects.append(Rect(0, lh+1, sr.w, sr.h))
                lh += sr.h + 1
                h += sr.h + 1
            
            h -= 1
            #h += 20
            
            frect = Rect(0, 0, w, h)

            monitor = glfw.get_primary_monitor()
            if m_scale := self.py_config.get("WINDOW_SCALE"):
                scale_x, scale_y = m_scale
            else:
                scale_x, scale_y = glfw.get_window_content_scale(self.window)
            
            if not DARWIN:
                scale_x, scale_y = 1.0, 1.0

            ww = int(w/scale_x)
            wh = int(h/scale_y)
            glfw.set_window_size(self.window, ww, wh)
            if pin := self.py_config.get("WINDOW_PIN", None):
                #monitor = glfw.get_window_monitor(self.window)
                work_rect = Rect(glfw.get_monitor_workarea(monitor))
                pinned = work_rect.take(ww, pin[0]).take(wh, pin[1])
                glfw.set_window_pos(self.window, pinned.x, pinned.y)

            GL.glClear(GL.GL_COLOR_BUFFER_BIT)

            if not self.context:
                self.context = skia.GrDirectContext.MakeGL()
                backend_render_target = skia.GrBackendRenderTarget(
                    int(w), int(h), 0, 0,
                    skia.GrGLFramebufferInfo(0, GL.GL_RGBA8))
                self.surface = skia.Surface.MakeFromBackendRenderTarget(
                    self.context,
                    backend_render_target,
                    skia.kBottomLeft_GrSurfaceOrigin,
                    skia.kRGBA_8888_ColorType,
                    skia.ColorSpace.MakeSRGB())
            
            assert self.surface is not None

            with self.surface as canvas:
                SkiaPen.CompositeToCanvas(DATPen().f(0.3).rect(frect), frect, canvas)

                for idx, (render, result, rp) in enumerate(self.previews_waiting_to_paint):
                    #result.translate(0, -rects[idx].y)
                    rect = rects[idx].offset((w-rects[idx].w)/2, 0)
                    self.draw_preview(dscale, canvas, rect, (render, result, rp))
            
            self.surface.flushAndSubmit()
            glfw.swap_buffers(self.window)
        
        self.previews_waiting_to_paint = []
        if self.server:
            self.server.serveonce()

    def draw_preview(self, scale, canvas, rect, waiter):
        if isinstance(waiter[1], Path) or isinstance(waiter[1], str):
            image = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(waiter[1])))
            if image:
                canvas.drawImage(image, rect.x, rect.y)
            return
        
        render, result, rp = waiter
        canvas.save()
        canvas.translate(rect.x, rect.y)
        canvas.scale(scale, scale)
        render.draw_preview(1.0, canvas, render.rect, result, rp)
        if hasattr(render, "blank_renderable"):
            paint = skia.Paint(AntiAlias=True, Color=coldtype.hsl(0, l=1, a=0.5).skia())
            canvas.drawString('Nothing found'.upper(), 315, 480, skia.Font(None, 20), paint)
        canvas.restore()
    
    def preload_frames(self, passes):
        for rp in passes:
            self.preloaded_frames.append(rp.output_path)
        self.playing_preloaded_frame = 0
    
    def on_modified(self, event):
        path = Path(event.src_path)
        if path in self.watchee_paths():
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
        print("... watching ...")
    
    def monitor_midi(self):
        controllers = {}
        for device, mi in self.midis:
            while msg := mi.getMessage(0):
                if self.args.midi_info:
                    print(device, msg)
                if msg.isNoteOn(): # Maybe not forever?
                    nn = msg.getNoteNumber()
                    action = self.midi_mapping[device]["note_on"].get(nn)
                    if action:
                        self.on_message({}, action)
                if msg.isController():
                    controllers[msg.getControllerNumber()] = msg.getControllerValue()/127
                    if self.args.midi_info:
                        print(">>>", msg.getControllerNumber(), msg.getControllerValue())
        
        if len(controllers) > 0:
            self.controller_values = {**self.controller_values, **controllers}
            self.on_action(Action.PreviewStoryboard, {})
            #print(self.controller_values)
    
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
        self.context.abandonContext()
        if self.hotkeys:
            self.hotkeys.stop()
        self.reset_renderers()
        self.stop_watching_file_changes()
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