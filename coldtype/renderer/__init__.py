import traceback, argparse, json, math, inspect
import sys, os, signal, tracemalloc, shutil, re
import pickle

import time as ptime
from pathlib import Path
from subprocess import Popen
from typing import Tuple, List
from random import shuffle, Random
from functools import partial

import coldtype
from coldtype.helpers import *

from coldtype.runon.path import P
from coldtype.geometry import Rect
from coldtype.text.reader import Font
from coldtype.pens.svgpen import SVGPen

from coldtype.renderable.tools import set_ffmpeg_command

from coldtype.renderer.config import ConfigOption
from coldtype.renderer.reader import SourceReader, run_source
from coldtype.renderer.state import RendererState
from coldtype.renderer.winman import Winmans, WinmanGLFWSkiaBackground
from coldtype.renderable import renderable, animation, Action, Overlay, runnable

from coldtype.renderer.keyboard import KeyboardShortcut

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
            parser.add_argument("inputs", nargs="*", help="Additional input files passed to renderable")
        for narg in nargs:
            parser.add_argument(narg[0], nargs="?", default=narg[1])
        
        pargs = dict(
            version=parser.add_argument("-v", "--version", action="store_true", default=False, help="Display version"),
            
            save_renders=parser.add_argument("-sv", "--save-renders", action="store_true", default=False, help="Should the renderer create image artifacts?"),
            
            rasterizer=parser.add_argument("-r", "--rasterizer", type=str, default=None, choices=["drawbot", "cairo", "svg", "skia", "pickle"], help="Which rasterization engine should coldtype use to create artifacts?"),

            cpu_render=parser.add_argument("-cpu", "--cpu-render", action="store_true", default=False, help="Should final rasters be performed without a GPU context?"),
            
            scale=parser.add_argument("-s", "--scale", type=float, default=1.0, help="When save-renders is engaged, what scale should images be rasterized at? (Useful for up-rezing)"),
            
            all=parser.add_argument("-a", "--all", action="store_true", default=False, help="If rendering an animation, pass the -a flag to render all frames sequentially"),

            render_directory=parser.add_argument("-rd", "--render-directory", action="store_true", default=False, help="kick off KeyboardShortcut.RenderDirectory straightaway and quit"),

            render_and_release=parser.add_argument("-rar", "--render-and-release", action="store_true", default=False, help="kick off KeyboardShortcut.RenderAndRelease straightaway and quit"),

            test_directory=parser.add_argument("-td", "--test-directory", action="store_true", default=False),

            build=parser.add_argument("-b", "--build", action="store_true", default=False, help="Should the build function be run and the renderer quit immediately?"),

            release=parser.add_argument("-rls", "--release", action="store_true", default=False, help="Should the release function be run and the renderer quit immediately?"),

            memory=parser.add_argument("-mm", "--memory", action="store_true", default=False, help="Show statistics about memory usage?"),

            is_subprocess=parser.add_argument("-isp", "--is-subprocess", action="store_true", default=False, help=argparse.SUPPRESS),

            config=parser.add_argument("-c", "--config", type=str, default=None, help="By default, Coldtype looks for a .coldtype.py file in ~ and the cwd; use this to override that and look at a specific file instead"),

            profile=parser.add_argument("-p", "--profile", type=str, default=None, help="What config profile do you want to use? Default is no profile"),

            cprofile=parser.add_argument("-cp", "--c-profile", action="store_true", default=False),
            
            format=parser.add_argument("-fmt", "--format", type=str, default=None, help="What image format should be saved to disk?"),

            indices=parser.add_argument("-i", "--indices", type=str, default=None),

            output_folder=parser.add_argument("-of", "--output-folder", type=str, default=None, help="If you don’t want to render to the default output location, specify that here."),

            show_exit_code=parser.add_argument("-sec", "--show-exit-code", action="store_true", default=False, help=argparse.SUPPRESS),

            frame_offset=parser.add_argument("-fo", "--frame-offset", type=int, default=0, help=argparse.SUPPRESS),

            viewer_solos=parser.add_argument("-vs", "--viewer-solos", type=str, default=None, help=argparse.SUPPRESS),

            last_cursor=parser.add_argument("-lc", "--last-cursor", type=str, default="0,0", help=argparse.SUPPRESS),

            k=parser.add_argument("-k", "--k", type=str, default=None, help=argparse.SUPPRESS)
        )

        ConfigOption.AddCommandLineArgs(pargs, parser)
        return pargs, parser

    def __init__(self, parser, winmans_class=Winmans):
        sys.path.insert(0, os.getcwd())

        self.subprocesses = {}

        if isinstance(parser, argparse.Namespace):
            self.args = parser
        else:
            self.args = parser.parse_args()

        if self.args.version:
            print(coldtype.__version__)
            self.dead = True
            return
        
        self._unnormalized_file = self.args.file
        
        normalized = self.prenormalize_filepath(self.args.file)
        if normalized == -1:
            self.dead = True
            return

        self.args.file = str(normalized)

        if self.on_args_parsed():
            self.dead = True
            return

        self._original_inputs = [*self.args.inputs]

        self.source_reader = SourceReader(
            renderer=self,
            inputs=self.args.inputs,
            cli_args=self.args)
        
        self.winmans = None
        self.winmans = winmans_class(self, self.source_reader.config)
        
        self.state = RendererState(self)

        self.watchees = []
        self.rasterizer_warning = None
        self.needs_new_context = False
        self.print_result_once = False

        self.extent = None
        
        if not self.reset_filepath(self.args.file if hasattr(self.args, "file") else None):
            self.dead = True
            return
        else:
            self.dead = False
        
        self.state.preview_scale = self.source_reader.config.preview_scale
        self.state.inputs = self.args.inputs
        self.exit_code = 0
        self.last_renders = []
        self.last_render_cleared = False

        set_ffmpeg_command(self.source_reader.config.ffmpeg_command)

        # for multiplex mode
        self.running_renderers = []
        self.completed_renderers = []

        self.action_waiting = None
        self.action_waiting_reason = None

        self.actions_queued = []
        self.debounced_actions = {}
        self.previews_waiting = []
        self.last_animation = None
        self.last_animations = []
        self.hotkeys = None
        self.hotkey_waiting = None
        self.stop_at_end = False

        if self.args.viewer_solos:
            self.viewer_solos = [int(x.strip()) for x in self.args.viewer_solos.split(",")]
        else:
            self.viewer_solos = []
        
        self.viewer_sample_frames = 1
        self.viewer_playback_rate = 1

    def on_args_parsed(self):
        pass
    
    def prenormalize_filepath(self, filepath):
        script = SourceReader.Script(filepath)
        if script:
            print(">>>", script)
            sr = SourceReader(renderer=self,
                inputs=self.args.inputs,
                cli_args=self.args)
            run_source(script, script, {}, {}, reader=sr)
            return -1
        else:
            return SourceReader.Demo(filepath)
    
    def reset_filepath(self, filepath, reload=False):
        dirdirection = 0
        if isinstance(filepath, int):
            dirdirection = filepath
            filepath = self.source_reader.filepath

        for _, cv2cap in self.state.cv2caps.items():
            cv2cap.release()
        
        self.state.frame_offset = 0
        self.state.cv2caps = {}

        root = Path(__file__).parent.parent
        
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
        self.watchees = []
        self.add_watchee([Watchable.Source, self.source_reader.filepath, None])

        ph = path_hash(self.source_reader.filepath)
        self.add_watchee([Watchable.Generic, Path(f"~/.coldtype/{ph}_input.json").expanduser(), None])
        
        if reload:
            self.reload_and_render(Action.Initial)
            self.actions_queued.append(Action.PreviewStoryboardReload)
            self.winmans.set_title(filepath.name)
            # TODO close an open blend file?

        return True

    def watchee_paths(self):
        return [w[1] for w in self.watchees]
    
    def print_error(self):
        stack = traceback.format_exc()
        print(stack)
        return stack.split("\n")[-2]
    
    def renderable_error(self, rect):
        short_error = self.print_error()
        
        r = rect
        render = renderable(r)
        res = P([
            P().rect(r).f(coldtype.Gradient.V(r,
                coldtype.hsl(_random.random(), l=0.3),
                coldtype.hsl(_random.random(), l=0.3)))])
        render.show_error = short_error
        return render, res

    def show_error(self):
        if self.state.playing > 0:
            self.state.playing = -1
        
        if (self.source_reader.config.no_viewer_errors
            or self.source_reader.config.no_viewer
            ): 
            short_error = self.print_error()
            bc_print(bcolors.FAIL, "SYNTAX ERROR")
            bc_print(bcolors.WARNING, short_error)
        else:
            render, res = self.renderable_error(self.extent)
            render._stacked_rect = self.extent
            self.previews_waiting.append([render, res, None])
    
    def show_message(self, message, scale=1):
        print(message)
    
    def play_sound(self, sound_name):
        if not self.source_reader.config.no_sound:
            play_sound(sound_name)

    def reload(self, trigger):
        if self.winmans.glsk:
            skfx.SKIA_CONTEXT = self.winmans.glsk.context
        
        self.last_animations = []

        if trigger == Action.Initial:
            self.state.frame_offset = self.args.frame_offset

        if True:
            self.state.reset()
            self.source_reader.reload(
                output_folder_override=self.args.output_folder)
            
            self.winmans.did_reload(self.source_reader.filepath, self.source_reader)
            
            try:
                for r in self.renderables(Action.PreviewStoryboardReload):
                    if isinstance(r, animation):
                        if not r.preview_only and not r.render_only:
                            self.last_animation = r
                        self.last_animations.append(r)
                    
                if self.last_animation:
                    self.winmans.did_reload_animation(self.last_animation)
            
                if trigger == Action.Initial:
                    if self.winmans.b3d:
                        self.winmans.b3d.launch(self.source_reader.blender_io())
            except SystemExit:
                self.on_exit(restart=False)
                return True
            except Exception as e:
                self.show_error()

            if self.last_animation:
                if self.last_animation.reset_to_zero:
                    self.state.frame_offset = 0
    
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
        if isinstance(render, runnable):
            return

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
    
    def renderables(self, trigger, previewing=False):
        _rs = self.source_reader.renderables(
            viewer_solos=self.viewer_solos,
            class_filters=[],
            previewing=previewing)
        
        for r in _rs:
            self.normalize_fmt(r)

            caps = r.cv2caps
            if caps is not None:
                import cv2
                for cap in caps:
                    if cap not in self.state.cv2caps:
                        self.state.cv2caps[cap] = cv2.VideoCapture(cap)

        return _rs
    
    def calculate_window_size(self, rs:List[renderable]):
        dscale = self.state.preview_scale
        w = 0
        llh = -1
        lh = -1
        h = 0
        for r in rs:
            if not hasattr(r, "rect"):
                continue
            
            sr = r.rect.scale(dscale, "mnx", "mny").round()
            w = max(sr.w, w)
            adjr = None
            if r.layer:
                adjr = Rect(0, llh, sr.w, sr.h)
            else:
                adjr = Rect(0, lh+1, sr.w, sr.h)
                llh = lh+1
                lh += sr.h + 1
                h += sr.h + 1
            r._stacked_rect = adjr.round()
        h -= 1

        extent = Rect(0, 0, w, h)

        if not self.extent:
            needs_new_context = True
        else:
            needs_new_context = self.extent != extent
        
        self.extent = extent
        
        #if needs_new_context:
        #    self.winmans.did_reset_extent(self.extent)

        return needs_new_context
    
    def _single_thread_render(self, trigger, indices=[], output_transform=None, no_sound=False, ditto_last=False) -> Tuple[int, int]:
        if not self.args.is_subprocess:
            start = ptime.time()

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

        if len(self.previews_waiting) > 0 and not rendering:
            return 0, 0, [], []

        def check_watches(render):
            for watch, flag in render.watch:
                if isinstance(watch, Font) and not watch.cacheable:
                    if watch.path not in self.watchee_paths():
                        self.add_watchee([Watchable.Font, watch.path, flag])
                    for ext in watch.font.getExternalFiles():
                        if ext not in self.watchee_paths():
                            self.add_watchee([Watchable.Font, ext, flag])
                elif watch not in self.watchee_paths():
                    self.add_watchee([Watchable.Generic, watch, flag])

        if previewing and self.source_reader.config.load_only:
            renders = self.renderables(trigger)
            for r in renders:
                check_watches(r)
            return 0, 0, 0, []

        if previewing and not self.source_reader.config.load_only:
            if Overlay.Rendered in self.state.overlays:
                overlays = []
                overlay_count = 0
                for render in self.last_renders:
                    if render.preview_only:
                        continue
                    overlays.append(render)
                    passes = render.passes(trigger, self.state, indices)
                    render.last_passes = passes
                    result = render.pass_path(passes[0].i)
                    self.previews_waiting.append([
                        render,
                        result,
                        passes[0]
                    ])
                    overlay_count += 1
                return overlay_count, 0, overlays, []

        self.state.previewing = previewing
        prev_renders = self.last_renders
        
        renders = self.renderables(trigger, previewing)

        self.last_renders = renders
        preview_count = 0
        render_count = 0
        collected_passes = []

        try:
            for render in renders:
                if isinstance(render, runnable):
                    render.run()
                    continue

                check_watches(render)
                
                passes = render.passes(trigger, self.state, indices)

                render.last_passes = passes
                
                for rp in passes:
                    collected_passes.append(rp)

                    output_path = rp.output_path
                    if output_transform:
                        output_path = output_transform(output_path)

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
                                        if pr.name == render.name and pr.last_result and pr.composites:
                                            render.last_result = pr.last_result
                            if render.single_frame and not render.interactable and render.last_result:
                                result = render.last_result
                            else:
                                result = render.normalize_result(render.run(rp, self.state))

                        if not result and not render.direct_draw:
                            #print(">>> No result")
                            result = P().rect(render.rect).f(None)

                        if previewing:
                            if render.direct_draw:
                                self.previews_waiting.append([render, None, rp])
                            else:
                                if render.single_frame and not render.interactable and render.last_result:
                                    preview_count += 1
                                    self.previews_waiting.append([render, result, rp])
                                else:
                                    if self.print_result_once or self.source_reader.config.print_result:
                                        self.print_result_once = False
                                        print("-"*90)
                                        print("@", ptime.time())
                                        result.print()
                                        print("\n" + "-"*90)
                                    
                                    preview_result = render.normalize_result(render.runpost(result, rp, self.state, self.source_reader.config))
                                    
                                    preview_count += 1
                                    if preview_result:
                                        self.previews_waiting.append([render, preview_result, rp])
                        
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
                                        show_render = self.rasterize(partial(render.run, rp, self.state), render, output_path, rp)
                                    else:
                                        show_render = self.rasterize(result or P(), render, output_path, rp)
                                    # TODO a progress bar?
                                    if show_render:
                                        try:
                                            print("<coldtype: saved: " + str(output_path.relative_to(Path.cwd())) + " >")
                                        except ValueError:
                                            print(">>> saved...", str(output_path))
                                
                                if ditto_last:
                                    copy_to = output_path.parent.parent / re.sub(r"\_[0-9]{4}\.png", "_last_render.png", output_path.name)
                                    print(">>>", output_path.name, re.sub(r"\_[0-9]{4}\.png", "_last_render.png", output_path.name))
                                    shutil.copy2(output_path, copy_to)
                                
                    except Exception as e:
                        #print(type(e))
                        self.show_error()
        except:
            self.show_error()
        
        if not self.args.is_subprocess and not previewing:
            print(f"<coldtype: render: {render_count}(" + str(round(ptime.time() - start, 3)) + "s)>")
        
        if len(self.actions_queued) > 0:
            no_sound = True
        
        if not previewing and not no_sound:
            if self.args.is_subprocess:
                self.play_sound("Morse")
            else:
                self.play_sound("Pop")
        
        return preview_count, render_count, renders, collected_passes

    def render(self, trigger, indices=[], ditto_last=False) -> Tuple[int, int]:
        #print(">RENDER!", trigger, self.action_waiting_reason)#, traceback.print_stack())

        if self.args.is_subprocess:
            if trigger != Action.RenderIndices:
                raise Exception("Invalid child process render action", trigger)
            else:
                p, r, _, _ = self._single_thread_render(trigger, indices=indices)
                self.exit_code = 5 # mark as child-process
                return p, r
        
        elif self.source_reader.config.multiplex and self.animation():
            if trigger in [Action.RenderAll, Action.RenderWorkarea]:
                all_frames = self.animation().all_frames()
                if trigger == Action.RenderAll:
                    frames = all_frames
                elif trigger == Action.RenderWorkarea:
                    anim = self.animation()
                    frames = anim.workarea()
                    if len(frames) == 0:
                        frames = all_frames
                self.render_multiplexed(frames)
                trigger = Action.RenderIndices
                indices = [0, all_frames[-1]] # always render first & last from main, to trigger a filesystem-change detection in premiere

        #elif self.animation() and trigger == Action.RenderWorkarea:
            #all_frames = self.animation().all_frames()
            #self._single_thread_render(Action.RenderIndices, [0, all_frames[-1]])
        
        preview_count, render_count, renders, passes = self._single_thread_render(trigger, indices, ditto_last=ditto_last)
        
        if not self.args.is_subprocess and render_count > 0:
            for render in renders:
                if hasattr(render, "package"):
                    result = render.package()
                else:
                    result = None
                
                if result:
                    self.previews_waiting.append([render, result, None])
                else:
                    self.action_waiting = Action.PreviewStoryboard
                    self.action_waiting_reason = "unclear"

            self.winmans.did_render(render_count, ditto_last, renders)
            
        did_render_fn = self.buildrelease_fn("didRender")
        if did_render_fn:
            did_render_fn(trigger, passes)
        
        if trigger == Action.RenderAll:
            did_render_all_fn = self.buildrelease_fn("didRenderAll")
            if did_render_all_fn:
                did_render_all_fn(passes)

        return preview_count, render_count
    
    def render_multiplexed(self, frames):
        start = ptime.time()

        tc = self.source_reader.config.thread_count
        print(f"<coldtype: thread-count:{tc}>")
        
        #group = math.floor(len(frames) / tc)
        ordered_frames = list(frames) #list(range(frames[0], frames[0]+len(frames)))
        shuffle(ordered_frames)

        import numpy as np
        subslices = np.array_split(ordered_frames, tc)
        #subslices = [list(s) for s in distribute(tc, ordered_frames)]
        
        self.reset_renderers()
        self.running_renderers = []
        self.completed_renderers = []

        for subslice in subslices:
            print(f"<coldtype: multiplex-slice:{len(subslice)}>")
            if len(subslice) == 0:
                continue
            sargs = [
                "coldtype",
                sys.argv[1],
                "-i", ",".join([str(s) for s in subslice]),
                "-isp",
                "-s", str(self.args.scale),
            ]
            
            if len(self.args.inputs) > 0:
                sargs = [*sargs[:2], *self.args.inputs, *sargs[2:]]
            
            if len(self.viewer_solos) > 0:
                sargs.append("-vs")
                sargs.append(",".join([str(x) for x in self.viewer_solos]))
            
            print(sargs)

            r = self.args.rasterizer
            if r:
                sargs.append("-r", r)
            if self.source_reader.config.no_sound:
                sargs.append("-ns", "1")
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

        print(f"<coldtype: multiplex-render ({str(round(ptime.time() - start, 3))})>")
        self.play_sound("Frog")
    
    def rasterize(self, content, render, path, rp):
        if render.self_rasterizing:
            print("Self rasterizing")
            return True
        
        did_rasterize = render.rasterize(self.source_reader.config, content, rp)
        if did_rasterize:
            return False
        
        scale = int(self.args.scale)
        rasterizer = self.args.rasterizer or render.rasterizer

        if rasterizer == "drawbot":
            from coldtype.pens.rendererdrawbotpen import RendererDrawBotPen
            RendererDrawBotPen.Composite(content, render.rect, str(path), scale=scale)
        elif rasterizer == "skia":
            if not skia:
                raise Exception("pip install skia-python")
            if render.fmt == "png":
                if render.composites:
                    content = content.ch(skfx.precompose(render.rect, scale=scale))
                    render.last_result = content
                
                ctx = None
                if self.winmans.glsk and self.winmans.glsk.context and not self.args.cpu_render:
                    ctx = self.winmans.glsk.context

                SkiaPen.Composite(content,
                    render.rect,
                    str(path),
                    scale=scale,
                    context=ctx,
                    style=render.style)
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
        
        return True
    
    def reload_and_render(self, trigger, watchable=None, indices=None):
        if (self.winmans.bg
            and not self.args.cpu_render
            and not self.winmans.glsk
            ):
            self.winmans.glsk = WinmanGLFWSkiaBackground(self.source_reader.config, self)

        wl = len(self.watchees)
        self.winmans.reset()

        try:
            should_halt = self.reload(trigger)
            if should_halt:
                return True
            if self.source_reader.program:
                renders = self.renderables(Action.Resave, previewing=True)
                self.needs_new_context = self.calculate_window_size(renders)
                if self.needs_new_context and trigger != Action.Initial:
                    self.debounced_actions["reset_extent"] = ptime.time()
                #if self.needs_new_context: #and trigger != Action.Initial:
                #    return True

                self.render(trigger, indices=indices)
                if self.state.playing < 0:
                    self.state.playing = 1
            else:
                print(">>>>>>>>>>>> No program loaded! <<<<<<<<<<<<<<")
        except:
            if not self.extent:
                self.extent = Rect(1200, 200)
                self.needs_new_context = True
            self.show_error()

    def main(self):
        self.profiler = None
        if self.args.c_profile:
            print(">>> profiling with cProfile...")
            import cProfile
            pr = cProfile.Profile()
            pr.enable()
            self.profiler = pr

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

    def start(self):
        should_halt = self.before_start()
        
        if not self.winmans.bg:
            self.initialize_gui_and_server()
        
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
            if not self.winmans.bg:
                if self.args.render_directory:
                    self.actions_queued.append(KeyboardShortcut.RenderDirectory)
                if self.args.render_and_release:
                    self.actions_queued.append(KeyboardShortcut.RenderAllAndRelease)
                    self.actions_queued.append(KeyboardShortcut.Kill)
                if self.args.test_directory:
                    self.actions_queued.append(KeyboardShortcut.TestDirectory)
                self.winmans.run_loop()
            else:
                self.on_exit()
    
    def before_start(self):
        pass

    def initialize_gui_and_server(self):
        self.winmans.add_viewers()

        if len(self.watchees) > 0:
            self.winmans.set_title(self.watchees[0][1].name)
        else:
            self.winmans.set_title("coldtype")

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
                self.action_waiting_reason = "on_message"
                #self.on_action(enum_action, message)
            else:
                print(">>> (", action, ") is not a recognized action")
    
    def jump_to_fn(self, fn_name):
        if self.last_animation:
            fi = self.last_animation.fn_to_frame(fn_name)
            if fi is None:
                print("fn_to_frame: no match")
                return False
            self.state.frame_offset = fi
            self.action_waiting = Action.PreviewStoryboard
            self.action_waiting_reason = "jump_to_fn"
            return True

    def lookup_action(self, action):
        return Action(action)
    
    def additional_actions(self):
        return []
    
    def collect_passes(self):
        trigger = Action.RenderAll
        renders = self.renderables(trigger)
        all_passes = []

        for render in renders:
            if not render.preview_only:
                all_passes.extend(render.passes(trigger, self.state, [0]))
        
        return all_passes
    
    def on_release(self, build=False, number=None):
        fnname = "build" if build else "release"
        if number is not None:
            fnname = "numpad"
        
        trigger = Action.RenderAll
        renders = self.renderables(trigger)

        attr_functions = []

        for render in renders:
            if hasattr(render, fnname) and getattr(render, fnname):
                attr_functions.append([render, getattr(render, fnname)])
                print(fnname, attr_functions[-1])
        
        fn = self.buildrelease_fn(fnname)
        
        if not fn and not attr_functions:
            if fnname == "release" and self.last_animation:
                print("DEFAULT RELEASE == ffmpeg mp4")
                fn = self.last_animation.export("h264", audio=self.last_animation.audio)
            else:
                print(f"No `{fnname}` fn defined in source")
                return
        
        if attr_functions:
            #print(">>>>>>>>>>>", attr_functions)
            def _fn(passes):
                for render, af in attr_functions:
                    res = af(render) # filter passes?
                    if callable(res):
                        res(passes)
            fn = _fn

        all_passes = self.collect_passes()
        try:
            if number is not None:
                fn = fn[number]

            arg_count = len(inspect.signature(fn).parameters)
            if arg_count == 0:
                res = fn()
            else:
                res = fn(all_passes)
            if isinstance(res, Action):
                return res
            
        except Exception as e:
            self.print_error()
            print("! Release failed !")
        
        print("/", fnname)
    
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
            self.state.frame_offset = 0
        elif shortcut == KeyboardShortcut.JumpEnd:
            self.state.frame_offset = -1
        
        elif shortcut == KeyboardShortcut.JumpPrev:
            self.state.frame_offset = self.last_animation.jump(self.state.frame_offset, -1)
        elif shortcut == KeyboardShortcut.JumpNext:
            self.state.frame_offset = self.last_animation.jump(self.state.frame_offset, +1)

        elif shortcut == KeyboardShortcut.ClearLastRender:
            return Action.ClearLastRender
        elif shortcut == KeyboardShortcut.ClearRenderedFrames:
            return Action.ClearRenderedFrames
        elif shortcut == KeyboardShortcut.ResetInitialMemory:
            self.state.memory = None
            #self.last_animation.write_reset_memory(self.state, self.last_animation.memory, True)
            return Action.PreviewStoryboard
        elif shortcut == KeyboardShortcut.ResetMemory:
            self.last_animation.write_reset_memory(self.state, self.last_animation.reset_memory, True)
            return Action.PreviewStoryboard
        
        elif shortcut == KeyboardShortcut.PlayRendered:
            self.winmans.toggle_rendered()
            self.actions_queued = [Action.PreviewStoryboard]
            return Action.PreviewPlay
        elif shortcut == KeyboardShortcut.PlayPreview:
            return Action.PreviewPlay
        elif shortcut == KeyboardShortcut.PlayToEnd:
            self.stop_at_end = True
            return Action.PreviewPlay
        elif shortcut == KeyboardShortcut.Echo:
            self.play_sound("Pop")
            return Action.PreviewStoryboard
        elif shortcut == KeyboardShortcut.EnableAudio:
            self.source_reader.config.enable_audio = not self.source_reader.config.enable_audio
            self.winmans.mod_title("audio",
                self.source_reader.config.enable_audio)
        
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
        elif shortcut == KeyboardShortcut.RenderAllAndPlay:
            self.on_action(Action.RenderAll)
            self.actions_queued.append(KeyboardShortcut.PlayRendered)
            return -1
        elif shortcut == KeyboardShortcut.RenderAllAndRelease:
            vs = self.state.versions
            if vs:
                for v in vs:
                    self.actions_queued.insert(0, KeyboardShortcut.CycleVersions)
                    self.actions_queued.insert(0, Action.Release)
                    self.actions_queued.insert(0, Action.RenderAll)
            else:
                self.on_action(Action.RenderAll)
                self.actions_queued.insert(0, Action.Release)
            #self.action_waiting = Action.Release
            #self.action_waiting_reason = shortcut
            return -1
        elif shortcut == KeyboardShortcut.RenderOne:
            la = self.last_animation
            self.on_action(Action.RenderIndices,
                [abs((self.state.frame_offset+la.offset) % la.duration)])
            return -1
        elif shortcut == KeyboardShortcut.RenderFrom:
            la = self.last_animation
            fo = abs((self.state.frame_offset+la.offset) % la.duration)
            idxs = list(range(fo, la.duration))
            self.on_action(Action.RenderIndices, idxs)
            return -1
        elif shortcut == KeyboardShortcut.RenderWorkarea:
            self.on_action(Action.RenderWorkarea)
            return -1
        elif shortcut == KeyboardShortcut.ToggleMultiplex:
            self.source_reader.config.multiplex = not self.source_reader.config.multiplex
            print(f"<coldtype: multiplexing={self.source_reader.config.multiplex}>")
            return -1
        
        elif shortcut == KeyboardShortcut.OverlayInfo:
            self.state.toggle_overlay(Overlay.Info)
        elif shortcut == KeyboardShortcut.OverlayTimeline:
            self.state.toggle_overlay(Overlay.Timeline)
        elif shortcut == KeyboardShortcut.OverlayRecording:
            self.state.toggle_overlay(Overlay.Recording)
        elif shortcut == KeyboardShortcut.OverlayRendered:
            self.winmans.toggle_rendered()
        
        elif shortcut == KeyboardShortcut.ToggleTimeViewer:
            self.source_reader.config.add_time_viewers = not self.source_reader.config.add_time_viewers
            return Action.PreviewStoryboardReload
        elif shortcut == KeyboardShortcut.ToggleXray:
            self.clear_last_render()
            self.source_reader.config.show_xray = not self.source_reader.config.show_xray
            return Action.PreviewStoryboard
        elif shortcut == KeyboardShortcut.ToggleGrid:
            self.clear_last_render()
            self.source_reader.config.show_grid = not self.source_reader.config.show_grid
            return Action.PreviewStoryboard
        
        elif shortcut == KeyboardShortcut.TogglePrintResult:
            self.clear_last_render()
            self.source_reader.config.print_result = not self.source_reader.config.print_result
            return Action.PreviewStoryboard
        elif shortcut == KeyboardShortcut.PrintResultOnce:
            self.clear_last_render()
            self.print_result_once = True
            return Action.PreviewStoryboard
        
        elif shortcut == KeyboardShortcut.PreviewScaleUp:
            return self.state.mod_preview_scale(+0.1)
        elif shortcut == KeyboardShortcut.PreviewScaleDown:
            return self.state.mod_preview_scale(-0.1)
        elif shortcut == KeyboardShortcut.PreviewScaleMin:
            return self.state.mod_preview_scale(0, 0.1)
        elif shortcut == KeyboardShortcut.PreviewScaleMax:
            return self.state.mod_preview_scale(0, 5)
        elif shortcut == KeyboardShortcut.PreviewScaleDefault:
            return self.state.mod_preview_scale(0, 1)

        elif shortcut == KeyboardShortcut.WindowOpacityDown:
            self.winmans.glsk.set_window_opacity(relative=-0.1)
        elif shortcut == KeyboardShortcut.WindowOpacityUp:
            self.winmans.glsk.set_window_opacity(relative=+0.1)
        elif shortcut == KeyboardShortcut.WindowOpacityMin:
            self.winmans.glsk.set_window_opacity(absolute=0.1)
        elif shortcut == KeyboardShortcut.WindowOpacityMax:
            self.winmans.glsk.set_window_opacity(absolute=1)
        
        elif shortcut == KeyboardShortcut.ViewerPlaybackSpeedIncrease:
            self.viewer_playback_rate = self.viewer_playback_rate * 2
        elif shortcut == KeyboardShortcut.ViewerPlaybackSpeedDecrease:
            self.viewer_playback_rate = self.viewer_playback_rate / 2
        
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
            folder = self.renderables(Action.PreviewStoryboard)[-1].output_folder
            folder.mkdir(parents=True, exist_ok=True)
            os.system(f"open {folder}")
        
        elif shortcut == KeyboardShortcut.ViewerTakeFocus:
            self.winmans.glsk.focus(force=True)
        
        elif shortcut == KeyboardShortcut.ViewerSoloNone:
            self.viewer_solos = []
            return Action.PreviewStoryboardReload
        elif shortcut == KeyboardShortcut.ViewerSoloNext:
            if len(self.viewer_solos):
                for i, solo in enumerate(self.viewer_solos):
                    self.viewer_solos[i] = solo + 1
            return Action.PreviewStoryboardReload
        elif shortcut == KeyboardShortcut.ViewerSoloPrev:
            if len(self.viewer_solos):
                for i, solo in enumerate(self.viewer_solos):
                    self.viewer_solos[i] = solo - 1
            return Action.PreviewStoryboardReload
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
            return Action.PreviewStoryboardReload
        elif shortcut == KeyboardShortcut.PrintApproxFPS:
            self.winmans.print_approx_fps = True
        elif shortcut.value.startswith("viewer_sample_frames"):
            self.viewer_sample_frames = int(shortcut.value.split("_")[-1])
        elif shortcut.value.startswith("viewer_numbered_action_"):
            action_number = int(shortcut.value.split("_")[-1])
            return self.on_release(number=action_number)
        elif shortcut == KeyboardShortcut.CopySVGToClipboard:
            self.winmans.glsk.copy_previews_to_clipboard = True
            return Action.PreviewStoryboard
        elif shortcut == KeyboardShortcut.RenderDirectory:
            adjs = self.buildrelease_fn("adjacents")
            if not adjs:
                adjs = self.source_reader.adjacents()
            else:
                adjs = adjs()

            for idx in range(0, len(adjs)):
                self.actions_queued.append(KeyboardShortcut.RenderAllAndRelease)
                #self.actions_queued.append(KeyboardShortcut.Release)

                if idx < (len(adjs) - 1):
                    self.actions_queued.append(KeyboardShortcut.LoadNextInDirectory)
                    self.actions_queued.append(Action.PreviewStoryboardReload)

            #return Action.Kill
            self.actions_queued.append(Action.Kill)

            return Action.PreviewStoryboardReload
        elif shortcut == KeyboardShortcut.CycleVersions:
            vi = self.source_reader.config.version_index
            versions = self.state.versions
            vi += 1
            if vi >= len(versions):
                vi = 0
            self.source_reader.config.version_index = vi
            return Action.PreviewStoryboardReload
        elif shortcut == KeyboardShortcut.Sleep:
            # just delays dequeuing next action by a frame
            return Action.PreviewStoryboard
        elif shortcut == KeyboardShortcut.TestDirectory:
            adjs = self.buildrelease_fn("adjacent")
            if not adjs:
                adjs = self.source_reader.adjacents()
            
            for _ in range(0, len(adjs)):
                self.actions_queued.append(KeyboardShortcut.LoadNextInDirectory)
                self.actions_queued.append(Action.PreviewStoryboardReload)
                for _ in range(0, self.source_reader.config.test_directory_delay):
                    self.actions_queued.append(KeyboardShortcut.Sleep)

            self.actions_queued.append(KeyboardShortcut.Kill)

            return Action.PreviewStoryboardReload
        elif shortcut in [
            KeyboardShortcut.LoadNextInDirectory,
            KeyboardShortcut.LoadPrevInDirectory,
            ]:
            self.args.frame_offset = 0
            d = -1 if shortcut == KeyboardShortcut.LoadPrevInDirectory else +1
            f = self.buildrelease_fn("adjacent")
            if f:
                res = f(d)
                if isinstance(res, Action):
                    return res
                elif isinstance(res, Path) or isinstance(res, str):
                    self.reset_filepath(res, reload=True)
            else:
                self.reset_filepath(d, reload=True)
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
            if editor_cmd == "code":
                if line is not None:
                    os.system(editor_cmd + " -g " + str(path) + ":" + str(line))
                else:
                    os.system(editor_cmd + " -g " + str(path))
            else:
                os.system(editor_cmd + " " + str(path))
    
    def on_shortcut(self, shortcut):
        waiting = self.shortcut_to_action(shortcut)
        if waiting:
            if waiting != -1:
                self.action_waiting = waiting
                self.action_waiting_reason = shortcut
        else:
            self.action_waiting = Action.PreviewStoryboard
            self.action_waiting_reason = "shortcut_default"

    def on_stdin(self, stdin):
        cmd, *args = stdin.split(" ")
        self.hotkey_waiting = (cmd, None, args)

    def on_action(self, action, message=None) -> bool:
        if isinstance(action, KeyboardShortcut):
            self.on_shortcut(self.action_waiting)
            return True

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
                self.winmans.toggle_playback()
            if action == Action.PreviewStoryboardPrevMany:
                self.winmans.frame_offset(-self.source_reader.config.many_increment)
            elif action == Action.PreviewStoryboardPrev:
                self.winmans.frame_offset(-self.viewer_sample_frames)
            elif action == Action.PreviewStoryboardNextMany:
                self.winmans.frame_offset(+self.source_reader.config.many_increment)
            elif action == Action.PreviewStoryboardNext:
                self.winmans.frame_offset(+self.viewer_sample_frames)
            self.render(Action.PreviewStoryboard)
        elif action == Action.Build:
            self.action_waiting = self.on_release(build=True)
            self.action_waiting_reason = "build"
        elif action == Action.Release:
            self.action_waiting = self.on_release()
            self.action_waiting_reason = "release"
        elif action == Action.RestartRenderer:
            self.on_exit(restart=True)
        elif action == Action.Kill:
            os.kill(os.getpid(), signal.SIGINT)
            #self.on_exit(restart=False)
        elif action == Action.ClearLastRender:
            self.clear_last_render()
            self.action_waiting = Action.PreviewStoryboard
            self.action_waiting_reason = "clear_last_render"
        elif action == Action.ClearRenderedFrames:
            for r in self.renderables(Action.PreviewStoryboard):
                shutil.rmtree(r.output_folder, ignore_errors=True)
            print("Deleted rendered version")
        else:
            return False
    
    def clear_last_render(self):
        self.last_render_cleared = True
        for r in self.renderables(Action.PreviewStoryboard):
            r.last_result = None
    
    def turn_over(self):
        if self.dead:
            self.on_exit()
            return
        
        if self.hotkey_waiting:
            self.execute_string_as_shortcut_or_action(*self.hotkey_waiting)
            self.hotkey_waiting = None
        
        now = ptime.time()
        
        if self.debounced_actions:
            now = ptime.time()
            for k, v in self.debounced_actions.items():
                if v:
                    if (now - v) > self.source_reader.config.debounce_time:
                        #self.action_waiting = Action.PreviewStoryboardReload
                        self.actions_queued.append(Action.PreviewStoryboardReload)
                        #self.action_waiting_reason = "debouncing"
                        self.debounced_actions[k] = None

        if self.action_waiting:
            action_in = self.action_waiting
            self.on_action(self.action_waiting)
            if action_in != self.action_waiting:
                # TODO should be recursive?
                self.on_action(self.action_waiting)
            self.action_waiting = None
            self.action_waiting_reason = None
        
        if len(self.actions_queued) > 0:
            self.action_waiting = self.actions_queued.pop(0)
            self.action_waiting_reason = "pop_from_queue"
        
        did_preview = self.winmans.turn_over()
        
        self.previews_waiting = []
        self.last_render_cleared = False

        if self.state.playing > 0:
            self.on_action(Action.PreviewStoryboardNext)
        
        for idx, (_, wp, flag, last_mod) in enumerate(self.watchees):
            wp:Path = wp
            if wp.exists():
                mtime = wp.stat().st_mtime
                if mtime > last_mod:
                    try:
                        print(f">>> resave: {wp.relative_to(Path.cwd())}")
                    except:
                        print(f">>> resave: {wp}")

                    self.watchees[idx][-1] = ptime.time()
                    self.on_modified(wp, flag)
                    return False
        
        return did_preview
    
    def on_modified(self, path, flag):
        #path = Path(event.src_path)
        #print("\n\n\n---\nMOD", path, ptime.time())

        actual_path = path
        if path.parent in self.watchee_paths():
            actual_path = path
            path = path.parent
        
        if True: #or path in self.watchee_paths():
            if path.suffix == ".json":
                if path.stem == "command" or "_input" in path.stem:
                    data = json.loads(path.read_text())
                    if "action" in data:
                        action = data.get("action")
                        if "filepath" in data:
                            path = data.get("filepath")
                            if path != str(self.last_animation.filepath):
                                print("IGNORING COMMAND")
                                return
                        self.hotkey_waiting = (action, None, data.get("args"))
                    return

                try:
                    json.loads(path.read_text())
                except json.JSONDecodeError:
                    print("Error decoding watched json", path)
                    return
            
            #idx = self.watchee_paths().index(path)
            #wpath, wtype, wflag = self.watchees[idx]
            
            if flag == "soft":
                self.action_waiting = Action.PreviewStoryboard
                self.action_waiting_reason = "soft_watch"
                return
            
            if flag == "restart":
                self.restart()
            
            if self.args.memory and process:
                memory = bytesto(process.memory_info().rss)
                diff = memory - self._last_memory
                self._last_memory = memory
                print(">>> pid:{:d}/new:{:04.2f}MB/total:{:4.2f}".format(os.getpid(), diff, memory))
            
            self.action_waiting = Action.PreviewStoryboardReload
            self.action_waiting_reason = "on_modified"
    
    def add_watchee(self, watchee):
        if self.args.is_subprocess:
            return

        watchee.append(ptime.time())
        self.watchees.append(watchee)
        if "_input.json" in str(watchee[1]):
            return
        
        try:
            print("    >>> watching...", watchee[1].relative_to(Path.cwd()))
        except Exception as e:
            #print(e)
            print("    >>> watching...", watchee[1])
    
    def execute_string_as_shortcut_or_action(self, shortcut, key, args=[]):
        #print("\n>>> shortcut:")
        #print(f"  \"{shortcut}\"({key if key else 'ø'}[{args}])\n")
        
        co = ConfigOption.ShortToConfigOption(shortcut)
        if co:
            if co == ConfigOption.WindowOpacity:
                self.winmans.glsk.set_window_opacity(absolute=args[0])
            else:
                print("> Unhandled ConfigOption", co, key)
            return
        
        if shortcut == "render_index":
            self.render(Action.RenderIndices, indices=[int(args[0])], ditto_last=True)
            return
        elif shortcut == "render_scratch":
            fi = int(args[0])
            print(f">/scratch:{fi}")
            def to_scratch(p):
                return Path(re.sub(r"[0-9]{4}", "XXXX", str(p)))
            self._single_thread_render(Action.RenderIndices, [fi], output_transform=to_scratch, no_sound=True)
            return

        try:
            ksc = KeyboardShortcut(shortcut)
        except ValueError:
            ksc = None
        
        if ksc:
            self.on_shortcut(KeyboardShortcut(shortcut))
        else:
            print("No shortcut/action", key, shortcut)
        
    def reset_renderers(self):
        for r in self.running_renderers:
            if r:
                r.terminate()
    
    def restart(self):
        print("> RESTARTING...")
        args = sys.argv
        if len(args) > 1:
            args[1] = str(self.source_reader.filepath)
            #args[1] = str(self._unnormalized_file)
        
        inputs = self.source_reader.program["__inputs__"]

        if len(inputs) > 0:
            if len(self._original_inputs) == len(inputs):
                for idx, input in enumerate(inputs):
                    args[idx+2] = input
            else:
                a_args = args[:2]
                b_args = args[len(self._original_inputs)+2:]
                args = a_args + inputs + b_args
                #print(">>>", a_args, "|||", b_args)
        
        # attempt to preserve state across reload

        fo = str(self.state.frame_offset)
        try:
            foi = args.index("-fo")
            args[foi+1] = fo
        except ValueError:
            args.append("-fo")
            args.append(fo)
        
        tv = str(int(self.source_reader.config.add_time_viewers or 0))
        try:
            tvi = args.index("-tv")
            args[tvi+1] = tv
        except ValueError:
            args.append("-tv")
            args.append(tv)
        
        x = str(int(self.source_reader.config.show_xray or 0))
        try:
            xi = args.index("-x")
            args[xi+1] = x
        except ValueError:
            args.append("-x")
            args.append(x)
        
        g = str(int(self.source_reader.config.show_grid or 0))
        try:
            gi = args.index("-g")
            args[gi+1] = g
        except ValueError:
            args.append("-g")
            args.append(g)
        
        vi = str(int(self.source_reader.config.version_index))
        try:
            vii = args.index("-vi")
            args[vii+1] = vi
        except ValueError:
            args.append("-vi")
            args.append(vi)
        
        lc = []
        for c in self.state.cursor_history[-3:]:
            lc.append(",".join([str(p) for p in c]))
        lc = ";".join(lc)
        try:
            lci = args.index("-lc")
            args[lci+1] = lc
        except ValueError:
            args.append("-lc")
            args.append(lc)
        
        print("> RESTART:", args)
        os.execl(sys.executable, *(["-m"]+args))

    def on_exit(self, restart=False):
        self.source_reader.unlink()

        for _, p in self.subprocesses.items():
            p.kill()

        self.winmans.terminate()
        
        if self.hotkeys:
            self.hotkeys.stop()
        
        self.reset_renderers()
        
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

        if self.profiler:
            print(">>>PROFILED!")
            print(self.profiler)
            self.profiler.disable()
            self.profiler.dump_stats("profile_result")


def main(winmans=Winmans):
    Path("~/.coldtype").expanduser().mkdir(exist_ok=True)
    _, parser = Renderer.Argparser()
    Renderer(parser, winmans_class=winmans).main()

if __name__ == "__main__":
    main()