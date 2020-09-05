import sys, os, re
from pathlib import Path

import asyncio, tempfile, websockets, traceback
import argparse, importlib, inspect, json, ast, math

import time as ptime
from enum import Enum
from typing import Tuple
from random import shuffle
from runpy import run_path
from subprocess import call, Popen

import coldtype
from coldtype.helpers import *
from coldtype.geometry import Rect
from coldtype.pens.svgpen import SVGPen
from coldtype.pens.cairopen import CairoPen
from coldtype.pens.drawbotpen import DrawBotPen
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.renderable import renderable, Action, animation
from coldtype.renderer.watchdog import AsyncWatchdog
from coldtype.viewer import PersistentPreview, WEBSOCKET_ADDR

try:
    import drawBot as db
except ImportError:
    db = None


class Watchable(Enum):
    Source = "Source"
    Font = "Font"
    Library = "Library"
    Generic = "Generic"


class EditAction(Enum):
    Newline = "newline"
    Tokenize = "tokenize"
    TokenizeLine = "tokenize_line"
    NewSection = "newsection"
    Capitalize = "capitalize"
    SelectWorkarea = "select_workarea"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def file_and_line_to_def(filepath, lineno):
    # https://julien.danjou.info/finding-definitions-from-a-source-file-and-a-line-number-in-python/
    candidate = None
    for item in ast.walk(ast.parse(filepath.read_text())):
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if item.lineno > lineno:
                continue
            if candidate:
                distance = lineno - item.lineno
                if distance < (lineno - candidate.lineno):
                    candidate = item
            else:
                candidate = item
    if candidate:
        return candidate.name


class Renderer():
    def Argparser(name="coldtype", file=True, nargs=[]):
        parser = argparse.ArgumentParser(prog=name, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        
        if file:
            parser.add_argument("file", type=str, nargs="?", help="The source file for a coldtype render")
        for narg in nargs:
            parser.add_argument(narg[0], nargs="?", default=narg[1])
        
        pargs = dict(
            version=parser.add_argument("-v", "--version", action="store_true", default=False, help="Display version"),

            watch=parser.add_argument("-w", "--watch", action="store_true", default=False, help="Watch for changes to source files"),
            
            save_renders=parser.add_argument("-sv", "--save-renders", action="store_true", default=False, help="Should the renderer create image artifacts?"),
            
            rasterizer=parser.add_argument("-r", "--rasterizer", type=str, default=None, choices=["drawbot", "cairo", "svg"], help="Which rasterization engine should coldtype use to create artifacts?"),
            
            scale=parser.add_argument("-s", "--scale", type=float, default=1.0, help="When save-renders is engaged, what scale should images be rasterized at? (Useful for up-rezing)"),
            
            all=parser.add_argument("-a", "--all", action="store_true", default=False, help="If rendering an animation, pass the -a flag to render all frames sequentially"),

            multiplex=parser.add_argument("-mp", "--multiplex", action="store_true", default=False, help="Render in multiple processes"),

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

            show_render_count=parser.add_argument("-src", "--show-render-count", action="store_true", default=False, help=argparse.SUPPRESS),
            
            reload_libraries=parser.add_argument("-rl", "--reload-libraries", action="store_true", default=False, help=argparse.SUPPRESS),

            drawbot=parser.add_argument("-db", "--drawbot", action="store_true", default=False, help=argparse.SUPPRESS))
        return pargs, parser

    def __init__(self, parser, no_socket_ok=False):
        sys.path.insert(0, os.getcwd())

        self.args = parser.parse_args()
        self.watchees = []
        self.reset_filepath(self.args.file if hasattr(self.args, "file") else None)
        self.layers = [l.strip() for l in self.args.layers.split(",")] if self.args.layers else []
        
        self.preview = PersistentPreview()
        if not no_socket_ok and not self.preview.ws:
            print(f"\n\n{bcolors.FAIL}! Please start the coldtype viewer app !{bcolors.ENDC}\n\n")
            raise Exception()
        
        self.preview.clear()
        self.program = None
        self.websocket = None
        self.exit_code = 0

        self.line_number = -1
        self.last_renders = []

        # for multiplex mode
        self.running_renderers = []
        self.completed_renderers = []

        self.observers = []

        self.reloadables = [
            #coldtype.pens.datpen,
            coldtype.text.reader,
            #coldtype.text.composer,
            coldtype.text,
            coldtype
        ]

        if self.args.reload_libraries:
            for r in self.reloadables:
                self.watchees.append([Watchable.Library, Path(r.__file__)])
    
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
        self.preview.send(f"<pre>{traceback.format_exc()}</pre>", None)
    
    def show_message(self, message, scale=1):
        self.preview.send(f"<pre style='background:hsla(150, 50%, 50%);transform:scale({scale})'>{message}</pre>")

    async def reload(self, trigger):
        try:
            load_drawbot = self.args.drawbot
            if load_drawbot:
                if not db:
                    raise Exception("Cannot run drawbot program without drawBot installed")
                else:
                    db.newDrawing()
            self.program = run_path(str(self.filepath))
            if load_drawbot:
                with tempfile.NamedTemporaryFile(suffix=".svg") as tf:
                    db.saveImage(tf.name)
                    self.preview.clear()
                    self.preview.send(f"<div class='drawbot-render'>{tf.read().decode('utf-8')}</div>", None)
                db.endDrawing()
            for k, v in self.program.items():
                if isinstance(v, coldtype.text.reader.Font):
                    await v.load()
                    if v.path not in self.watchee_paths():
                        self.watchees.append([Watchable.Font, v.path])
                    for ext in v.font.getExternalFiles():
                        if ext not in self.watchee_paths():
                            self.watchees.append([Watchable.Font, ext])
                elif isinstance(v, DefconFont):
                    p = Path(v.path).resolve()
                    if p not in self.watchee_paths():
                        self.watchees.append([Watchable.Font, p])
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
            if isinstance(v, renderable):
                _rs.append(v)
        if self.args.filter_functions:
            function_names = [f.strip() for f in self.args.filter_functions.split(",")]
            _rs = [r for r in _rs if r.func.__name__ in function_names]
        if self.args.monitor_lines and trigger != Action.RenderAll:
            func_name = file_and_line_to_def(self.filepath, self.line_number)
            matches = [r for r in _rs if r.func.__name__ == func_name]
            if len(matches) > 0:
                return matches
        return _rs
    
    async def _single_thread_render(self, trigger, indices=[]) -> Tuple[int, int]:
        renders = self.renderables(trigger)
        for render in renders:
            render.preview = self.preview
        self.last_renders = renders
        preview_count = 0
        render_count = 0
        try:
            for render in renders:
                for watch in render.watch:
                    if watch not in self.watchee_paths():
                        self.watchees.append([Watchable.Font, watch])

                if self.args.output_folder:
                    output_folder = Path(self.args.output_folder).expanduser().resolve()
                elif render.dst:
                    output_folder = render.dst / (render.custom_folder or render.folder(self.filepath))
                else:
                    output_folder = self.filepath.parent / "renders" / (render.custom_folder or render.folder(self.filepath))
                did_render = False
                prefix = self.args.file_prefix or render.prefix or self.filepath.stem
                fmt = self.args.format or render.fmt
                _layers = self.layers if len(self.layers) > 0 else render.layers
                for rp in render.passes(trigger, _layers, indices):
                    output_path = output_folder / f"{prefix}_{rp.suffix}.{fmt}"
                    rp.output_path = output_path
                    rp.action = trigger

                    try:
                        result = await render.run(rp)
                        try:
                            if len(result) == 2 and isinstance(result[1], str):
                                self.show_message(result[1])
                                result = result[0]
                        except:
                            pass
                        if trigger in [
                            Action.Initial,
                            Action.Resave,
                            Action.PreviewStoryboard,
                            Action.PreviewIndices,
                        ]:
                            preview_result = await render.runpost(result, rp)
                            preview_count += 1
                            if preview_result:
                                render.send_preview(self.preview, preview_result, rp)
                        
                        if self.args.save_renders or trigger in [
                            Action.RenderAll,
                            Action.RenderWorkarea,
                            Action.RenderIndices,
                        ]:
                            did_render = True
                            if len(render.layers) > 0:
                                for layer in render.layers:
                                    for layer_result in result:
                                        layer_tag = layer_result.getTag()
                                        if layer == layer_tag:
                                            if layer_tag != "__default__":
                                                layer_folder = render.layer_folder(self.filepath, layer)
                                                output_path = output_folder / layer_folder / f"{prefix}_{layer}_{rp.suffix}.{fmt}"
                                                output_path.parent.mkdir(exist_ok=True, parents=True)
                                            else:
                                                output_path = rp.output_path
                                            render_count += 1
                                            self.rasterize(layer_result, render, output_path)
                                            print(">>> saved layer...", str(output_path.relative_to(Path.cwd())))
                            else:
                                render_count += 1
                                output_path.parent.mkdir(exist_ok=True, parents=True)
                                if render.self_rasterizing:
                                    print(">>> self-rasterized...", output_path)
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
        
        return preview_count, render_count

    async def render(self, trigger, indices=[]) -> Tuple[int, int]:
        if self.args.is_subprocess: # is a child process of a multiplexed render
            if trigger != Action.RenderIndices:
                raise Exception("Invalid child process render action")
                return 0, 0
            else:
                p, r = await self._single_thread_render(trigger, indices=indices)
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
        
        preview_count, render_count = await self._single_thread_render(trigger, indices)
        
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
            DrawBotPen.Composite(content, render.rect, str(path), scale=scale)
        elif rasterizer == "svg":
            path.write_text(SVGPen.Composite(content, render.rect, viewBox=True))
        elif rasterizer == "cairo":
            CairoPen.Composite(content, render.rect, str(path), scale=scale)
        else:
            raise Exception(f"rasterizer ({rasterizer}) not supported")
    
    async def reload_and_render(self, trigger, watchable=None, indices=None):
        wl = len(self.watchees)

        if self.args.reload_libraries and watchable == Watchable.Library:
            # TODO limit this to what actually changed?
            print("> reloading reloadables...")
            try:
                for m in self.reloadables:
                    importlib.reload(m)
            except:
                self.show_error()

        try:
            await self.reload(trigger)
            if self.program:
                self.preview.clear()
                preview_count, render_count = await self.render(trigger, indices=indices)
                if self.args.show_render_count:
                    print("render>", preview_count, "/", render_count)
            else:
                self.preview.send("<pre>No program loaded!</pre>")
        except:
            self.show_error()

        if wl < len(self.watchees) and len(self.observers) > 0:
            from pprint import pprint
            pprint(self.watchees)
            self.stop_watching_file_changes()
            self.watch_file_changes()

    def main(self):
        try:
            asyncio.get_event_loop().run_until_complete(self.start())
        except KeyboardInterrupt:
            print("INTERRUPT")
            self.on_exit()
        if self.args.show_exit_code:
            print("exit>", self.exit_code)
        sys.exit(self.exit_code)

    async def start(self):
        if self.args.version:
            print(">>>", coldtype.__version__)
            should_halt = True
        else:
            should_halt = await self.before_start()
        
        if should_halt:
            self.on_exit()
        else:
            if self.args.all:
                await self.reload_and_render(Action.RenderAll)
            elif self.args.indices:
                indices = [int(x.strip()) for x in self.args.indices.split(",")]
                await self.reload_and_render(Action.RenderIndices, indices=indices)
            else:
                await self.reload_and_render(Action.Initial)
            await self.on_start()
            if self.args.watch:
                loop = asyncio.get_running_loop()
                self.watch_file_changes()
                await asyncio.gather(
                    self.listen_to_ws(),
                    self.listen_to_stdin()
                )
            else:
                self.on_exit()
    
    async def before_start(self):
        pass

    async def on_start(self):
        pass
    
    async def on_message(self, message, action):
        if action:
            enum_action = self.lookup_action(action)
            if enum_action:
                await self.on_action(enum_action, message)
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
        else:
            return None, None

    async def on_stdin(self, stdin):
        action, data = self.stdin_to_action(stdin)
        if action:
            if action == Action.PreviewIndices:
                self.preview.clear()
                await self.render(action, indices=data)
            else:
                await self.on_action(action)

    async def on_action(self, action, message=None) -> bool:
        if action in [Action.PreviewStoryboard, Action.RenderAll, Action.RenderWorkarea]:
            await self.reload_and_render(action)
            return True
        elif action in [Action.PreviewStoryboardNext, Action.PreviewStoryboardPrev]:
            increment = 1 if action == Action.PreviewStoryboardNext else -1
            for render in self.last_renders:
                if hasattr(render, "storyboard"):
                    for idx, fidx in enumerate(render.storyboard):
                        nidx = (fidx + increment) % render.duration
                        render.storyboard[idx] = nidx
                    self.preview.clear()
                    await self.render(Action.PreviewStoryboard)
            return True
        elif action == Action.ArbitraryCommand:
            await self.on_stdin(message.get("input"))
            return True
        elif action == Action.UICallback:
            for render in self.renderables(action):
                if render.ui_callback:
                    render.ui_callback(message)
        elif message.get("serialization"):
            await asyncio.sleep(1)
            await self.reload(Action.Resave)
            print(">>>>>>>>>>>", self.animation().timeline.cti)
            cw = self.animation().timeline.find_workarea()
            print("WORKAREA", cw)
            if cw:
                start, end = cw
                self.send_to_external(None, workarea_update=True, start=start, end=end)
            else:
                print("No CTI/trackGroups found")
        elif message.get("trigger_from_app"):
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
            self.preview.send(json.dumps(kwargs), full=True)
    
    async def process_ws_message(self, message):
        try:
            jdata = json.loads(message)
            action = jdata.get("action")
            if action:
                await self.on_message(jdata, jdata.get("action"))
            elif jdata.get("metadata") and jdata.get("path"):
                path = Path(jdata.get("path"))
                if self.args.monitor_lines and path == self.filepath:
                    self.line_number = jdata.get("line_number")
        except:
            self.show_error()
            print("Malformed message", message)

    async def listen_to_ws(self):
        async with websockets.connect(WEBSOCKET_ADDR) as websocket:
            self.websocket = websocket
            async for message in websocket:
                await self.process_ws_message(message)
    
    async def listen_to_stdin(self):
        async for line in self.stream_as_generator(sys.stdin):
            await self.on_stdin(line.decode("utf-8").strip())

    async def stream_as_generator(self, stream):
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader(loop=loop)
        reader_protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: reader_protocol, stream)

        while True:
            line = await reader.readline()
            if not line:  # EOF.
                break
            yield line
    
    async def on_modified(self, event):
        path = Path(event.src_path)
        if path in self.watchee_paths():
            idx = self.watchee_paths().index(path)
            print(f">>> resave: {Path(event.src_path).relative_to(Path.cwd())}")
            await self.reload_and_render(Action.Resave, self.watchees[idx][0])

    def watch_file_changes(self):
        self.observers = []
        dirs = set([w[1].parent for w in self.watchees])
        for d in dirs:
            o = AsyncWatchdog(str(d), on_modified=self.on_modified, recursive=False)
            o.start()
            self.observers.append(o)
        print("... watching ...")
    
    def stop_watching_file_changes(self):
        for o in self.observers:
            o.stop()
        
    def reset_renderers(self):
        for r in self.running_renderers:
            if r:
                r.terminate()

    def on_exit(self):
        #if self.args.watch:
        #    print(f"<EXIT RENDERER ({exit_code})>")
        self.reset_renderers()
        self.stop_watching_file_changes()
        self.preview.close()

def main():
    pargs, parser = Renderer.Argparser()
    Renderer(parser).main()

if __name__ == "__main__":
    main()