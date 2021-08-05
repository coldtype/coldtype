import traceback, threading
import argparse, json, math
import sys, os, signal, tracemalloc, shutil
import platform, pickle

try:
    import numpy as np
except ImportError:
    np = None

import time as ptime
from pathlib import Path
from typing import Tuple
from pprint import pprint
from runpy import run_path
from subprocess import Popen, PIPE, STDOUT
from random import shuffle, Random
from more_itertools import distribute
from functools import partial

from http.server import HTTPServer

import coldtype
from coldtype.helpers import *
from coldtype.geometry import Rect
from coldtype.text.reader import Font

from coldtype.renderer.winman import WinmanGLFWSkia, WinmanGLFWSkiaBackground, WinmanPassthrough, glfw, WinmanWebview

from coldtype.renderer.config import ConfigOption
from coldtype.renderer.reader import SourceReader
from coldtype.renderer.state import RendererState, Keylayer, Overlay
from coldtype.renderable import renderable, Action, animation
from coldtype.pens.datpen import DATPen, DATPens

from coldtype.pens.svgpen import SVGPen
from coldtype.pens.jsonpen import JSONPen

from coldtype.renderer.midi import MIDIWatcher
from coldtype.renderer.keyboard import KeyboardShortcut

try:
    from coldtype.renderer.watchdog import AsyncWatchdog
except ImportError:
    AsyncWatchdog = None

try:
    import skia
    from coldtype.pens.skiapen import SkiaPen
    import coldtype.fx.skia as skfx
except ImportError:
    skia = None
    SkiaPen = None

try:
    import drawBot as db
except ImportError:
    db = None

from coldtype.renderer.utils import *

_random = Random()

from time import sleep, time

try:
    import psutil
    process = psutil.Process(os.getpid())
except ImportError:
    process = None


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
            
            save_renders=parser.add_argument("-sv", "--save-renders", action="store_true", default=False, help="Should the renderer create image artifacts?"),
            
            rasterizer=parser.add_argument("-r", "--rasterizer", type=str, default=None, choices=["drawbot", "cairo", "svg", "skia", "pickle"], help="Which rasterization engine should coldtype use to create artifacts?"),

            cpu_render=parser.add_argument("-cpu", "--cpu-render", action="store_true", default=False, help="Should final rasters be performed without a GPU context?"),
            
            scale=parser.add_argument("-s", "--scale", type=float, default=1.0, help="When save-renders is engaged, what scale should images be rasterized at? (Useful for up-rezing)"),
            
            all=parser.add_argument("-a", "--all", action="store_true", default=False, help="If rendering an animation, pass the -a flag to render all frames sequentially"),

            build=parser.add_argument("-b", "--build", action="store_true", default=False, help="Should the build function be run and the renderer quit immediately?"),

            release=parser.add_argument("-rls", "--release", action="store_true", default=False, help="Should the release function be run and the renderer quit immediately?"),

            memory=parser.add_argument("-mm", "--memory", action="store_true", default=False, help="Show statistics about memory usage?"),

            show_time=parser.add_argument("-st", "--show-time", action="store_true", default=False, help="Show time for each render"),

            is_subprocess=parser.add_argument("-isp", "--is-subprocess", action="store_true", default=False, help=argparse.SUPPRESS),

            no_sound=parser.add_argument("-ns", "--no-sound", action="store_true", default=False, help="Don’t make sound"),

            config=parser.add_argument("-c", "--config", type=str, default=None, help="By default, Coldtype looks for a .coldtype.py file in ~ and the cwd; use this to override that and look at a specific file instead"),

            profile=parser.add_argument("-p", "--profile", type=str, default=None, help="What config profile do you want to use? Default is no profile"),
            
            format=parser.add_argument("-fmt", "--format", type=str, default=None, help="What image format should be saved to disk?"),

            indices=parser.add_argument("-i", "--indices", type=str, default=None),

            output_folder=parser.add_argument("-of", "--output-folder", type=str, default=None, help="If you don’t want to render to the default output location, specify that here."),

            filter_functions=parser.add_argument("-ff", "--filter-functions", type=str, default=None, help="Names of functions to render"),

            hide_keybuffer=parser.add_argument("-hkb", "--hide-keybuffer", action="store_true", default=False, help="Should the keybuffer be shown?"),

            show_exit_code=parser.add_argument("-sec", "--show-exit-code", action="store_true", default=False, help=argparse.SUPPRESS),

            show_render_count=parser.add_argument("-src", "--show-render-count", action="store_true", default=False, help=argparse.SUPPRESS),

            frame_offsets=parser.add_argument("-fo", "--frame-offsets", type=str, default=None, help=argparse.SUPPRESS),
        )

        ConfigOption.AddCommandLineArgs(pargs, parser)
        return pargs, parser

    def __init__(self, parser, no_socket_ok=False):
        sys.path.insert(0, os.getcwd())

        self.subprocesses = {}
        self.parser = parser
        self.args = parser.parse_args()

        if self.args.version:
            print(">>>", coldtype.__version__)
            self.dead = True
            return

        self.winman = WinmanPassthrough()
        self.source_reader = SourceReader(
            renderer=self, cli_args=self.args)

        if self.args.is_subprocess or self.args.all or self.args.release or self.args.build:
            self.args.no_watch = True
        
        if not self.source_reader.config.webviewer and not skia and not glfw:
            print("No viewing renderer installed — rendering all...")
            sleep(1)
        
        self.state = RendererState(self)

        self.observers = []
        self.watchees = []
        self.watchee_mods = {}
        self.rasterizer_warning = None
        
        if not self.reset_filepath(self.args.file if hasattr(self.args, "file") else None):
            self.dead = True
            return
        else:
            self.dead = False
        
        self.state.preview_scale = self.source_reader.config.preview_scale
        self.exit_code = 0
        self.line_number = -1
        self.last_renders = []
        self.last_render_cleared = False

        # for multiplex mode
        self.running_renderers = []
        self.completed_renderers = []

        self.action_waiting = None
        self.debounced_actions = {}
        self.requests_waiting = []
        self.waiting_to_render = []
        self.previews_waiting_to_paint = []
        self.last_animation = None
        self.playing = 0
        self.hotkeys = None
        self.hotkey_waiting = None

        if self.args.filter_functions:
            self.function_filters = [f.strip() for f in self.args.filter_functions.split(",")]
        else:
            self.function_filters = []

        self.recurring_actions = {}
        self.viewer_solos = []
    
    def reset_filepath(self, filepath, reload=False):
        dirdirection = 0
        if isinstance(filepath, int):
            dirdirection = filepath
            filepath = self.source_reader.filepath

        for k, cv2cap in self.state.cv2caps.items():
            cv2cap.release()

        self.line_number = -1
        self.stop_watching_file_changes()
        self.state.input_history.clear()
        self.state._frame_offsets = {}
        self.state._initial_frame_offsets = {}
        self.state.cv2caps = {}

        root = Path(__file__).parent.parent
        pj = False

        if not filepath:
            filepath = root / "demo/demo.py" # should not be demo
        elif filepath == "demo": # TODO more of these
            filepath = root / "demo/demo.py"
        elif filepath == "blank":
            filepath = root / "demo/blank.py"
        elif filepath == "boiler":
            filepath = root / "demo/boiler.py"
        elif filepath == "pj":
            pj = True
            filepath = root / "renderer/picklejar.py"
        
        filepath = self.source_reader.normalize_filepath(filepath)

        if not filepath.exists():
            if filepath.suffix == ".py":
                print(">>> That python file does not exist...")
                create = input(">>> Do you want to create it and add some coldtype boilerplate? (y/n): ")
                if create.lower() == "y":
                    filepath.parent.mkdir(exist_ok=True, parents=True)
                    filepath.write_text((root / "demo/boiler.py").read_text())
                    self.open_in_editor(filepath)
            else:
                raise Exception("That file does not exist")
        
        self._codepath_offset = 0
        filepath = self.source_reader.reset_filepath(filepath, reload=False, dirdirection=dirdirection)
        # TODO check exists here on filepath
        self.watchees = [[Watchable.Source, self.source_reader.filepath, None]]

        self.watchees.append([Watchable.Generic, Path("~/.coldtype/command.json").expanduser(), None])

        if pj:
            self.watchees.append([Watchable.Generic, Path("~/.coldtype/picklejar"), None])

        if not self.args.is_subprocess and not self.source_reader.config.no_viewer:
            self.watch_file_changes()
        
        if reload:
            self.reload_and_render(Action.PreviewStoryboard)
            self.winman.set_title(filepath.name)

        return True
    
    def launch_blender_watch(self, blend_files):
        if "blender_watch" in self.subprocesses:
            self.subprocesses["blender_watch"].kill()
            del self.subprocesses["blender_watch"]

        from coldtype.blender.render import blender_launch_livecode
        blend_file = blend_files[0]
        self.subprocesses["blender_watch"] = blender_launch_livecode(blend_file)

    def watchee_paths(self):
        return [w[1] for w in self.watchees]
    
    def print_error(self):
        stack = traceback.format_exc()
        print(stack)
        return stack.split("\n")[-2]
    
    def renderable_error(self):
        short_error = self.print_error()
        
        r = Rect(1200, 300)
        render = renderable(r)
        res = DATPens([
            DATPen().rect(r).f(coldtype.Gradient.V(r,
            coldtype.hsl(_random.random(), l=0.3),
            coldtype.hsl(_random.random(), l=0.3))),
        ])
        render.show_error = short_error
        return render, res

    def show_error(self):
        if self.playing > 0:
            self.playing = -1
        render, res = self.renderable_error()
        self.previews_waiting_to_paint.append([render, res, None])
    
    def show_message(self, message, scale=1):
        print(message)

    def reload(self, trigger):
        if skia and SkiaPen:
            skfx.SKIA_CONTEXT = self.winman.context

        if True:
            self.state.reset()
            self.source_reader.reload()
            
            if self.source_reader.config.blender_watch:
                cb = Path("~/.coldtype/blender.txt").expanduser()
                if cb.exists():
                    cb.unlink()
                cb.write_text(f"import,{str(self.source_reader.filepath)}")
            
            try:
                full_restart = False
                blend_files = []

                for r in self.renderables(Action.PreviewStoryboardReload):
                    if hasattr(r, "blend"):
                        blend_files.append(r.blend)

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
                
                if full_restart:
                    fos = {}
                    if self.args.frame_offsets:
                        fos = eval(self.args.frame_offsets)
                        for k, v in fos.items():
                            self.state.adjust_keyed_frame_offsets(k, lambda i, o: v[i])
                    
                if self.source_reader.program.get("COLDTYPE_NO_WATCH"):
                    return True
                                
                if self.source_reader.config.blender_watch and trigger == Action.Initial and len(blend_files) > 0:
                    self.launch_blender_watch(blend_files)
                
            except SystemExit:
                self.on_exit(restart=False)
                return True
            except Exception as e:
                self.show_error()
    
    def animation(self):
        renderables = self.renderables(Action.PreviewStoryboard)
        for r in renderables:
            if isinstance(r, animation):
                return r
    
    def buildrelease_fn(self, fnname="release"):
        candidate = None
        for k, v in self.source_reader.program.items():
            if k == fnname:
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
        _rs = self.source_reader.renderables(
            viewer_solos=self.viewer_solos,
            function_filters=self.function_filters,
            class_filters=[],
            output_folder_override=self.args.output_folder)
        
        for r in _rs:
            self.normalize_fmt(r)

            caps = r.cv2caps
            if caps is not None:
                import cv2
                for cap in caps:
                    if cap not in self.state.cv2caps:
                        self.state.cv2caps[cap] = cv2.VideoCapture(cap)

        if len(_rs) == 0:
            root = Path(__file__).parent.parent
            sr = SourceReader(root / "demo/blank.py")
            _rs = sr.renderables()
            sr.unlink()
        return _rs
    
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
        try:
            for render in renders:
                for watch, flag in render.watch:
                    if isinstance(watch, Font) and not watch.cacheable:
                        if watch.path not in self.watchee_paths():
                            self.watchees.append([Watchable.Font, watch.path, flag])
                        for ext in watch.font.getExternalFiles():
                            if ext not in self.watchee_paths():
                                self.watchees.append([Watchable.Font, ext, flag])
                    elif watch not in self.watchee_paths():
                        self.watchees.append([Watchable.Generic, watch, flag])
                
                passes = render.passes(trigger, self.state, indices)
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
                self.state.preview_scale = self.winman.preview_scale()
                
                for rp in passes:
                    output_path = rp.output_path

                    if rendering and render.preview_only:
                        continue

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
                            if False:
                                pass
                            else:
                                if render.preview_only:
                                    continue
                                render_count += 1
                                output_path.parent.mkdir(exist_ok=True, parents=True)
                                if render.self_rasterizing:
                                    try:
                                        print(">>> self-rasterized...", output_path.relative_to(Path.cwd()))
                                    except ValueError:
                                        print(">>> self-rasterized...", output_path)
                                else:
                                    if render.direct_draw:
                                        self.rasterize(partial(render.run, rp, self.state), render, output_path)
                                    else:
                                        self.rasterize(result or DATPen(), render, output_path)
                                    # TODO a progress bar?
                                    try:
                                        print(">>> saved...", str(output_path.relative_to(Path.cwd())))
                                    except ValueError:
                                        print(">>> saved...", str(output_path))
                    except Exception as e:
                        #print(type(e))
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
        
        elif self.source_reader.config.multiplex and self.animation():
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
                result = render.package()
                if result:
                    self.previews_waiting_to_paint.append([render, result, None])
                else:
                    self.action_waiting = Action.PreviewStoryboard

            self.send_to_external(None, rendered=True)

        return preview_count, render_count
    
    def render_multiplexed(self, frames):
        start = ptime.time()

        tc = self.source_reader.config.thread_count
        print(">>> THREAD_COUNT", tc)
        
        group = math.floor(len(frames) / tc)
        ordered_frames = list(frames) #list(range(frames[0], frames[0]+len(frames)))
        shuffle(ordered_frames)
        #subslices = list(chunks(ordered_frames, group))
        subslices = [list(s) for s in distribute(tc, ordered_frames)]

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
            from coldtype.pens.rendererdrawbotpen import RendererDrawBotPen
            RendererDrawBotPen.Composite(content, render.rect, str(path), scale=scale)
        elif rasterizer == "skia":
            if not skia:
                raise Exception("pip install skia-python")
            if render.fmt == "png":
                content = content.ch(skfx.precompose(render.rect))
                render.last_result = content
                if render.bg_render:
                    content = DATPens([
                        DATPen().rect(render.rect).f(render.bg),
                        content
                    ])
                SkiaPen.Composite(content, render.rect, str(path), scale=scale, context=None if self.args.cpu_render else self.winman.context, style=render.style)
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
            self.winman = WinmanGLFWSkiaBackground(self.source_reader.config, self)

        wl = len(self.watchees)
        self.winman.reset()

        try:
            should_halt = self.reload(trigger)
            if should_halt:
                return True
            if self.source_reader.program:
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
            self.start()
        except KeyboardInterrupt:
            self.on_exit()
        if self.args.show_exit_code:
            print("exit>", self.exit_code)
        sys.exit(self.exit_code)
    
    def initialize_gui_and_server(self):
        ws_port = self.source_reader.config.websocket_port

        if self.source_reader.config.websocket or self.source_reader.config.webviewer:
            self.server = run_echo_server(ws_port, "daemon_websocket")
        else:
            self.server = None
        
        if self.source_reader.config.webviewer:
            WinmanWebview(self.source_reader.config, self)
        
        elif not glfw and not skia:
            print("\n\n>>> To run the coldtype viewer, you’ll need to install with the [viewer] optional package, ala `pip install coldtype[viewer]`\n\n")

        if glfw and not self.source_reader.config.no_viewer:
            self.winman = WinmanGLFWSkia(self.source_reader.config, self)
            self.typeface = skia.Typeface.MakeFromFile(str(sibling(__file__, "../demo/RecMono-CasualItalic.ttf")))

        self.midi = MIDIWatcher(
            self.source_reader.config,
            self.state,
            self.execute_string_as_shortcut_or_action)

        if len(self.watchees) > 0:
            self.winman.set_title(self.watchees[0][1].name)
        else:
            self.winman.set_title("coldtype")

        self.hotkeys = None
        try:
            if self.source_reader.config.hotkeys:
                from pynput import keyboard
                mapping = {}
                for k, v in self.source_reader.config.hotkeys.items():
                    mapping[k] = partial(self.on_hotkey, k, v)
                self.hotkeys = keyboard.GlobalHotKeys(mapping)
                self.hotkeys.start()
        except:
            pass

    def start(self):
        should_halt = self.before_start()
        
        if not self.args.no_watch:
            self.initialize_gui_and_server()
        else:
            self.server = None
        
        if should_halt:
            self.on_exit()
        else:
            if self.args.all:
                self.reload_and_render(Action.RenderAll)
                if self.args.build:
                    self.on_release(build=1)
                if self.args.release:
                    self.on_release()
            elif self.args.build:
                self.reload_and_render(Action.RenderIndices, indices=[0])
                self.on_release(build=1)
                if self.args.release:
                    self.on_release()
            elif self.args.release:
                self.reload_and_render(Action.RenderIndices, indices=[0])
                self.on_release()
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
                if glfw and not self.source_reader.config.no_viewer:
                    self.winman.listen()
                elif self.source_reader.config.webviewer:
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
        self.hotkey_waiting = (action, key_combo, None)
    
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
    
    def on_release(self, build=False):
        fnname = "build" if build else "release"
        release_fn = self.buildrelease_fn(fnname)
        if not release_fn:
            print(f"No `{fnname}` fn defined in source")
            return
        trigger = Action.RenderAll
        renders = self.renderables(trigger)
        all_passes = []
        try:
            for render in renders:
                if not render.preview_only:
                    all_passes.extend(render.passes(trigger, self.state, [0]))

            release_fn(all_passes)
        except Exception as e:
            self.print_error()
            print("! Release failed !")
    
    def shortcut_to_action(self, shortcut):
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
            self.on_action(Action.RenderedPlay)
            return -1
        elif shortcut == KeyboardShortcut.PlayPreview:
            self.winman.stop_playing_preloaded()
            return Action.PreviewPlay
        elif shortcut == KeyboardShortcut.PlayPreviewSlow:
            if shortcut not in self.recurring_actions:
                self.recurring_actions[shortcut] = dict(
                    interval=0.5,
                    action=KeyboardShortcut.PreviewNext,
                    last=0)
            else:
                del self.recurring_actions[shortcut]
        
        elif shortcut == KeyboardShortcut.ReloadSource:
            return Action.PreviewStoryboardReload
        elif shortcut == KeyboardShortcut.RestartApp:
            self.on_action(Action.RestartRenderer)
            return -1
        elif shortcut == KeyboardShortcut.Kill:
            os.kill(os.getpid(), signal.SIGINT)
            os.system(f"kill {os.getpid()}")
            return -1
        elif shortcut == KeyboardShortcut.Quit:
            self.dead = True
            return -1
        
        elif shortcut == KeyboardShortcut.Release:
            self.on_action(Action.Release)
            return -1
        elif shortcut == KeyboardShortcut.Build:
            self.on_action(Action.Build)
            return -1
        elif shortcut == KeyboardShortcut.RenderAll:
            self.on_action(Action.RenderAll)
            return -1
        elif shortcut == KeyboardShortcut.RenderOne:
            fo = [abs(o%self.last_animation.duration) for o in self.state.get_frame_offsets(self.last_animation.name)]
            # TODO should iterate over all animations, not just "last" (but infra isn't there for this yet)
            self.on_action(Action.RenderIndices, fo)
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
        elif shortcut == KeyboardShortcut.OverlayRendered:
            self.state.toggle_overlay(Overlay.Rendered)
        
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
            self.winman.set_window_opacity(relative=-0.1)
        elif shortcut == KeyboardShortcut.WindowOpacityUp:
            self.winman.set_window_opacity(relative=+0.1)
        elif shortcut == KeyboardShortcut.WindowOpacityMin:
            self.winman.set_window_opacity(absolute=0.1)
        elif shortcut == KeyboardShortcut.WindowOpacityMax:
            self.winman.set_window_opacity(absolute=1)
        
        elif shortcut == KeyboardShortcut.MIDIControllersPersist:
            self.state.persist()
        elif shortcut == KeyboardShortcut.MIDIControllersClear:
            self.state.clear()
        elif shortcut == KeyboardShortcut.MIDIControllersReset:
            self.state.reset(ignore_current_state=True)
        
        elif shortcut == KeyboardShortcut.JumpToFrameFunctionDef:
            frame = self.last_animation._active_frames(self.state)[0]
            fn_prefix, fn_context = self.last_animation.frame_to_fn(frame)
            original_code = self.source_reader.filepath.read_text().splitlines()
            found_line = -1
            for li, line in enumerate(original_code):
                if line.strip().startswith(fn_prefix):
                    found_line = li
            self.open_in_editor(line=found_line)
        
        elif shortcut == KeyboardShortcut.OpenInEditor:
            self.open_in_editor()
        
        elif shortcut == KeyboardShortcut.ShowInFinder:
            os.system(f"open {self.last_animation.output_folder}")
        
        elif shortcut == KeyboardShortcut.ViewerTakeFocus:
            if not self.winman.focus():
                self.open_in_editor()
        
        elif shortcut == KeyboardShortcut.ViewerSoloNone:
            self.viewer_solos = []
        elif shortcut == KeyboardShortcut.ViewerSoloNext:
            if len(self.viewer_solos):
                for i, solo in enumerate(self.viewer_solos):
                    self.viewer_solos[i] = solo + 1
        elif shortcut == KeyboardShortcut.ViewerSoloPrev:
            if len(self.viewer_solos):
                for i, solo in enumerate(self.viewer_solos):
                    self.viewer_solos[i] = solo - 1
        elif shortcut in [
            KeyboardShortcut.ViewerSolo1,
            KeyboardShortcut.ViewerSolo2,
            KeyboardShortcut.ViewerSolo3,
            KeyboardShortcut.ViewerSolo4,
            KeyboardShortcut.ViewerSolo5,
            KeyboardShortcut.ViewerSolo6,
            KeyboardShortcut.ViewerSolo7,
            KeyboardShortcut.ViewerSolo8,
            KeyboardShortcut.ViewerSolo9
            ]:
            self.viewer_solos = [int(str(shortcut)[-1])-1]
        elif shortcut == KeyboardShortcut.CopySVGToClipboard:
            self.winman.copy_previews_to_clipboard = True
            return Action.PreviewStoryboard
        elif shortcut == KeyboardShortcut.LoadNextInDirectory:
            self.reset_filepath(+1, reload=True)
        elif shortcut == KeyboardShortcut.LoadPrevInDirectory:
            self.reset_filepath(-1, reload=True)
        else:
            print(shortcut, "not recognized")
    
    def open_in_editor(self, filepath=None, line=None):
        if filepath is None:
            filepath = self.source_reader.filepath
        
        try:
            path = filepath.relative_to(Path.cwd())
        except ValueError:
            path = filepath
        
        editor_cmd = self.source_reader.config.editor_command
        if editor_cmd:
            if line is not None:
                os.system(editor_cmd + " -g " + str(path) + ":" + str(line))
            else:
                os.system(editor_cmd + " -g " + str(path))
    
    def on_shortcut(self, shortcut):
        waiting = self.shortcut_to_action(shortcut)
        if waiting:
            if waiting != -1:
                self.action_waiting = waiting
        else:
            self.action_waiting = Action.PreviewStoryboard

    def on_stdin(self, stdin):
        cmd, *args = stdin.split(" ")
        self.hotkey_waiting = (cmd, None, args)

    def on_action(self, action, message=None) -> bool:
        if action in [
            Action.RenderAll,
            Action.RenderWorkarea,
            Action.PreviewStoryboardReload
            ]:
            self.reload_and_render(action)
            return True
        elif action in [Action.RenderIndices]:
            self.reload_and_render(action, indices=message)
        elif action in [Action.PreviewStoryboard]:
            self.render(Action.PreviewStoryboard)
        elif action in [
            Action.PreviewStoryboardNextMany,
            Action.PreviewStoryboardPrevMany,
            Action.PreviewStoryboardNext,
            Action.PreviewStoryboardPrev,
            Action.PreviewPlay]:
            if action == Action.PreviewPlay:
                self.winman.stop_playing_preloaded()
                if self.playing == 0:
                    self.playing = 1
                else:
                    self.playing = 0
            if action == Action.PreviewStoryboardPrevMany:
                self.state.adjust_all_frame_offsets(-self.source_reader.config.many_increment)
            elif action == Action.PreviewStoryboardPrev:
                self.state.adjust_all_frame_offsets(-1)
            elif action == Action.PreviewStoryboardNextMany:
                self.state.adjust_all_frame_offsets(+self.source_reader.config.many_increment)
            elif action == Action.PreviewStoryboardNext:
                self.state.adjust_all_frame_offsets(+1)
            self.render(Action.PreviewStoryboard)
        elif action == Action.RenderedPlay:
            self.playing = 0
            self.winman.toggle_play_preloaded()
        elif action == Action.Build:
            self.on_release(build=True)
        elif action == Action.Release:
            self.on_release()
        elif action == Action.RestartRenderer:
            self.on_exit(restart=True)
        elif action == Action.Kill:
            os.kill(os.getpid(), signal.SIGINT)
            #self.on_exit(restart=False)
        elif action == Action.ToggleMultiplex:
            self.source_reader.config.multiplex = not self.source_reader.config.multiplex
            print(">>> MULTIPLEXING?", self.source_reader.config.multiplex)
        elif action == Action.ClearLastRender:
            self.last_render_cleared = True
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
        
        animation = self.animation()
        if animation and animation.timeline:
            print("EVENT", action, kwargs)
            if action:
                kwargs["action"] = action.value
            kwargs["prefix"] = self.source_reader.filepath.stem
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
        
        return []
    
    def turn_over(self):
        to_delete = []
        for k, sb in self.subprocesses.items():
            returncode = sb.poll()
            if returncode is not None:
                if k == "blender_watch": #and returncode != 0:
                    self.launch_blender_watch()
                    self.action_waiting = Action.PreviewStoryboardReload
                else:
                    to_delete.append(k)
        
        for k in to_delete:
            del self.subprocesses[k]

        if self.dead:
            self.on_exit()
            return
        
        if self.hotkey_waiting:
            self.execute_string_as_shortcut_or_action(*self.hotkey_waiting)
            self.hotkey_waiting = None
        
        now = ptime.time()
        for k, v in self.watchee_mods.items():
            if v and (now - v) > 1:
                #print("CAUGHT ONE")
                self.action_waiting = Action.PreviewStoryboard
                self.watchee_mods[k] = None
        
        if self.debounced_actions:
            now = ptime.time()
            for k, v in self.debounced_actions.items():
                if v:
                    if (now - v) > self.source_reader.config.debounce_time:
                        self.action_waiting = Action.PreviewStoryboardReload
                        self.debounced_actions[k] = None

        if self.action_waiting:
            action_in = self.action_waiting
            self.on_action(self.action_waiting)
            if action_in != self.action_waiting:
                # TODO should be recursive?
                self.on_action(self.action_waiting)
            self.action_waiting = None
        
        if self.server:
            msgs = []
            for k, v in self.server.connections.items():
                if hasattr(v, "messages") and len(v.messages) > 0:
                    for msg in v.messages:
                        msgs.append(msg)
                    v.messages = []
            
            for msg in msgs:
                self.process_ws_message(msg)

        if self.midi.monitor(self.playing):
            self.action_waiting = Action.PreviewStoryboard
        
        if glfw and not self.source_reader.config.no_viewer:
            did_preview = self.winman.turn_over()
        
        if self.source_reader.config.webviewer:
            did_preview = self.turn_over_webviewer()
        
        self.state.needs_display = 0
        self.previews_waiting_to_paint = []
        self.last_render_cleared = False
    
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
        
        return did_preview

    def draw_preview(self, idx, scale, canvas, rect, waiter):
        if isinstance(waiter[1], Path) or isinstance(waiter[1], str):
            image = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(waiter[1])))
            if image:
                canvas.drawImage(image, rect.x, rect.y)
            return
        
        render, result, rp = waiter
        error_color = coldtype.rgb(1, 1, 1).skia()
        canvas.save()
        canvas.translate(0, self.winman.window_scrolly)
        canvas.translate(rect.x, rect.y)
        
        if not self.source_reader.config.window_transparent:
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
                short_error = self.print_error()
                render.show_error = short_error
                error_color = coldtype.rgb(0, 0, 0).skia()
        else:
            if render.composites:
                comp = result.ch(skfx.precompose(render.rect))
                if not self.last_render_cleared:
                    render.last_result = comp
                else:
                    render.last_result = None
            else:
                comp = result
            
            #print("DRAW---\n", comp.tree())
            render.draw_preview(1.0, canvas, render.rect, comp, rp)
        
        if hasattr(render, "show_error"):
            paint = skia.Paint(AntiAlias=True, Color=error_color)
            canvas.drawString(render.show_error, 30, 70, skia.Font(self.typeface, 50), paint)
            canvas.drawString("> See process in terminal for traceback", 30, 120, skia.Font(self.typeface, 32), paint)
        
        canvas.restore()
    
    def on_modified(self, event):
        path = Path(event.src_path)
        #print(path, path.parent, path.parent.stem)

        if path.parent.stem == "picklejar":
            if path.exists():
                self.debounced_actions["picklejar"] = ptime.time()
            return

        #return
        actual_path = path
        if path.parent in self.watchee_paths():
            actual_path = path
            path = path.parent
        if path in self.watchee_paths():
            if path.suffix == ".json":
                if path.stem == "command":
                    data = json.loads(path.read_text())
                    if "action" in data:
                        action = data.get("action")
                        self.hotkey_waiting = (action, None, None)
                    return

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
            
            idx = self.watchee_paths().index(path)
            wpath, wtype, wflag = self.watchees[idx]
            if wflag == "soft":
                self.state.watch_soft_mods[actual_path] = True
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
        if self.args.no_watch:
            return None
        
        if not AsyncWatchdog:
            print("> must install watchdog to watch files")
            return None

        self.observers = []
        dirs = set([w[1] if w[1].is_dir() else w[1].parent for w in self.watchees])
        for d in dirs:
            o = AsyncWatchdog(str(d), on_modified=self.on_modified, recursive=True)
            o.start()
            self.observers.append(o)
        if self.source_reader.filepath:
            try:
                print(f"... watching {self.source_reader.filepath.relative_to(Path.cwd())} for changes ...")
            except ValueError:
                print(f"... watching {self.source_reader.filepath} for changes ...")
    
    def execute_string_as_shortcut_or_action(self, shortcut, key, args=[]):
        print("SHORTCUT", shortcut, key, args)
        co = ConfigOption.ShortToConfigOption(shortcut)
        if co:
            if co == ConfigOption.WindowOpacity:
                self.winman.set_window_opacity(absolute=args[0])
            else:
                print("> Unhandled ConfigOption", co, key)
            return

        try:
            ksc = KeyboardShortcut(shortcut)
            ea = None
        except ValueError:
            try:
                ksc = None
                ea = EditAction(shortcut)
            except ValueError:
                ea = None
        
        if ksc:
            self.on_shortcut(KeyboardShortcut(shortcut))
        elif ea:
            self.on_action(EditAction(shortcut), {})
        elif not ea:
            print("No shortcut/action", key, shortcut)
    
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

        args[1] = str(self.source_reader.filepath)
        
        # attempt to preserve state across reload
        fo = str(self.state._frame_offsets)
        try:
            foi = args.index("-fo")
            args[foi+1] = fo
        except ValueError:
            args.append("-fo")
            args.append(fo)
        
        print("> RESTART:", args)
        os.execl(sys.executable, *(["-m"]+args))

    def on_exit(self, restart=False):
        self.source_reader.unlink()

        for _, p in self.subprocesses.items():
            p.kill()

        self.winman.terminate()
        
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
            self.restart()


def main():
    Path("~/.coldtype").expanduser().mkdir(exist_ok=True)
    pargs, parser = Renderer.Argparser()
    Renderer(parser).main()

if __name__ == "__main__":
    main()