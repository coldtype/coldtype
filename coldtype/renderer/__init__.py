import sys, os
from pathlib import Path

import asyncio
import websockets

from coldtype.renderer.watchdog import AsyncWatchdog

import traceback
from subprocess import call
from runpy import run_path
import argparse
import importlib
import inspect
import json
from enum import Enum

import coldtype
from coldtype import renderable
from coldtype.geometry import Rect
from coldtype.pens.svgpen import SVGPen
from coldtype.pens.cairopen import CairoPen
from coldtype.pens.drawbotpen import DrawBotPen
from coldtype.viewer import PersistentPreview, WEBSOCKET_ADDR
from coldtype.animation import animation, Frame

class Watchable(Enum):
    Source = "Source"
    Font = "Font"
    Library = "Library"


class Renderer():
    def Argparser(name="coldtype", file=True, nargs=[]):
        parser = argparse.ArgumentParser(prog=name, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        
        if file:
            parser.add_argument("file", type=str, help="The source file for a coldtype render")
        for narg in nargs:
            parser.add_argument(narg[0], nargs="?", default=narg[1])
        
        parser.add_argument("-w", "--watch", action="store_true", default=False, help="Watch for changes to source files")
        
        parser.add_argument("-sv", "--save-renders", action="store_true", default=False, help="Should the renderer create image artifacts?")

        parser.add_argument("-r", "--rasterizer", type=str, default="drawbot", choices=["drawbot", "cairo", "svg"], help="Which rasterization engine should coldtype use to create artifacts?")
        
        parser.add_argument("-s", "--scale", type=float, default=1.0, help="When save-renders is engaged, what scale should images be rasterized at? (Useful for up-rezing)")

        parser.add_argument("-a", "--all", action="store_true", default=False, help="If rendering an animation, pass the -a flag to render all frames sequentially")

        parser.add_argument("-fmt", "--format", type=str, default="png", help="What image format should be saved to disk?")
        
        parser.add_argument("-rl", "--reload-libraries", action="store_true", default=False, help=argparse.SUPPRESS)
        
        return parser

    def __init__(self, parser):
        self.args = parser.parse_args()
        self.watchees = []
        self.reset_filepath(self.args.file if hasattr(self.args, "file") else None)
        
        self.preview = PersistentPreview()
        self.preview.clear()
        self.program = None
        self.websocket = None
        self.exit_code = 0

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

    async def reload(self, trigger):
        try:
            self.program = run_path(str(self.filepath))
            for k, v in self.program.items():
                if isinstance(v, coldtype.text.reader.Font):
                    await v.load()
                    if v.path not in self.watchee_paths():
                        self.watchees.append([Watchable.Font, v.path])
                    for ext in v.font.getExternalFiles():
                        if ext not in self.watchee_paths():
                            self.watchees.append([Watchable.Font, ext])
        except Exception as e:
            self.program = None
            self.show_error()
    
    def renderables(self):
        _rs = []
        for k, v in self.program.items():
            if isinstance(v, renderable):
                _rs.append(v)
            elif isinstance(v, animation):
                _rs.append(v)
        return _rs

    async def render(self, trigger):
        page = self.program.get("page", None)
        renders = self.program.get("renders")
        if renders and len(renders) > 0:
            renders = renders
        else:
            renders = self.renderables()
        render_data = self.program.get("render_data", {})
        try:
            for render in renders:
                if isinstance(render, renderable):
                    rect = render.rect
                    args = [render.rect]
                    render_fn = render.func
                    suffices = [render.func.__name__]
                    folder = ""
                elif isinstance(render, animation):
                    rect = render.rect
                    args = []
                    suffices = []
                    frames = render.storyboard
                    if trigger == "render_all":
                        frames = list(range(0, render.duration))
                    for x in frames:
                        args.append(Frame(x, render))
                        suffices.append("{:04d}".format(x))
                    render_fn = render.func
                    folder = f"{self.filepath.stem}/{render_fn.__name__}/"
                else:
                    rect = page
                    args = [rect]
                    render_fn = render
                    suffices = [render.__name__]
                    folder = ""
                
                results = []
                if inspect.iscoroutinefunction(render_fn):
                    for arg in args:
                        results.append(await render_fn(arg))
                else:
                    for arg in args:
                        results.append(render_fn(arg))
                
                did_render = False
                for idx, result in enumerate(results):
                    if trigger in ["initial", "render_storyboard", "resave"]:
                        self.preview.send(SVGPen.Composite(result, rect, viewBox=True), bg=render_data.get("bg", 1), max_width=800)
                    if self.args.save_renders or trigger in ["render_all"]:
                        did_render = True
                        output_path = self.filepath.parent / "renders" / f"{folder}{self.filepath.stem}_{suffices[idx]}.{self.args.format}"
                        output_path.parent.mkdir(exist_ok=True, parents=True)
                        self.rasterize(result, rect, output_path)
                        print(">>> saved...", output_path.name)
                if did_render:
                    print(">>> DONE!")
        except:
            self.show_error()
    
    def rasterize(self, content, frame, path):
        scale = int(self.args.scale)
        if self.args.rasterizer == "drawbot":
            DrawBotPen.Composite(content, frame, str(path), scale=scale)
        elif self.args.rasterizer == "svg":
            path.write_text(SVGPen.Composite(content, frame, viewBox=True))
        else:
            CairoPen.Composite(content, frame, str(path), scale=scale)
    
    async def reload_and_render(self, trigger, watchable=None):
        wl = len(self.watchees)
        self.preview.clear()

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
                await self.render(trigger)
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
            self.on_exit(0)
        print(">", self.exit_code)
        sys.exit(self.exit_code)

    async def start(self):
        should_halt = await self.before_start()
        if should_halt:
            self.on_exit(0)
        else:
            await self.reload_and_render("render_all" if self.args.all else "initial")
            exit_code = await self.on_start()
            if not exit_code:
                exit_code = 0
            if self.args.watch:
                loop = asyncio.get_running_loop()
                self.watch_file_changes()
                await asyncio.gather(self.listen_to_ws())
            else:
                self.on_exit(exit_code)
    
    async def before_start(self):
        pass

    async def on_start(self):
        pass
    
    async def on_message(self, message, action):
        if action:
            await self.on_action(action, message)
    
    async def on_action(self, action, message):
        if action == "render_storyboard":
            await self.reload_and_render(action)
        elif action == "render_all":
            await self.reload_and_render(action)
    
    async def process_ws_message(self, message):
        try:
            jdata = json.loads(message)
            await self.on_message(jdata, jdata.get("action"))
        except:
            print("Malformed message", message)

    async def listen_to_ws(self):
        async with websockets.connect(WEBSOCKET_ADDR) as websocket:
            self.websocket = websocket
            async for message in websocket:
                await self.process_ws_message(message)
    
    async def on_modified(self, event):
        path = Path(event.src_path)
        if path in self.watchee_paths():
            idx = self.watchee_paths().index(path)
            print(f">>> resave ...{event.src_path[-25:]}")
            await self.reload_and_render("resave", self.watchees[idx][0])

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

    def on_exit(self, exit_code):
        if self.args.watch:
            print(f"<EXIT RENDERER ({exit_code})>")
        self.stop_watching_file_changes()
        self.preview.close()
        self.exit_code = exit_code

def main():
    Renderer(Renderer.Argparser()).main()

if __name__ == "__main__":
    main()