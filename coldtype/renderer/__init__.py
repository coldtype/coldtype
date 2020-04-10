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
import ast
from enum import Enum

import coldtype
from coldtype.helpers import *
from coldtype import renderable
from coldtype.geometry import Rect
from coldtype.pens.svgpen import SVGPen
from coldtype.pens.cairopen import CairoPen
from coldtype.pens.drawbotpen import DrawBotPen
from coldtype.viewer import PersistentPreview, WEBSOCKET_ADDR


class Watchable(Enum):
    Source = "Source"
    Font = "Font"
    Library = "Library"


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
            parser.add_argument("file", type=str, help="The source file for a coldtype render")
        for narg in nargs:
            parser.add_argument(narg[0], nargs="?", default=narg[1])
        
        pargs = dict(
            watch=parser.add_argument("-w", "--watch", action="store_true", default=False, help="Watch for changes to source files"),
            
            save_renders=parser.add_argument("-sv", "--save-renders", action="store_true", default=False, help="Should the renderer create image artifacts?"),
            
            rasterizer=parser.add_argument("-r", "--rasterizer", type=str, default=None, choices=["drawbot", "cairo", "svg"], help="Which rasterization engine should coldtype use to create artifacts?"),
            
            scale=parser.add_argument("-s", "--scale", type=float, default=1.0, help="When save-renders is engaged, what scale should images be rasterized at? (Useful for up-rezing)"),
            
            all=parser.add_argument("-a", "--all", action="store_true", default=False, help="If rendering an animation, pass the -a flag to render all frames sequentially"),
            
            format=parser.add_argument("-fmt", "--format", type=str, default=None, help="What image format should be saved to disk?"),

            file_prefix=parser.add_argument("-fp", "--file-prefix", type=str, default="", help="Should the output files be prefixed with something? If so, put it here."),

            output_folder=parser.add_argument("-of", "--output-folder", type=str, default=None, help="If you don’t want to render to the default output location, specify that here."),

            monitor_lines=parser.add_argument("-ml", "--monitor-lines", action="store_true", default=False, help=argparse.SUPPRESS),

            filter_functions=parser.add_argument("-ff", "--filter-functions", type=str, default=None, help="Names of functions to render"),
            
            reload_libraries=parser.add_argument("-rl", "--reload-libraries", action="store_true", default=False, help=argparse.SUPPRESS))
        return pargs, parser

    def __init__(self, parser):
        self.args = parser.parse_args()
        self.watchees = []
        self.reset_filepath(self.args.file if hasattr(self.args, "file") else None)
        
        self.preview = PersistentPreview()
        self.preview.clear()
        self.program = None
        self.websocket = None
        self.exit_code = 0

        self.line_number = -1
        self.last_renders = []

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
    
    def show_message(self, message):
        self.preview.send(f"<pre style='background:hsla(150, 50%, 50%)'>{message}</pre>")

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
    
    def renderables(self, trigger):
        _rs = []
        for k, v in self.program.items():
            if isinstance(v, renderable):
                _rs.append(v)
        if self.args.filter_functions:
            function_names = [f.strip() for f in self.args.filter_functions.split(",")]
            _rs = [r for r in _rs if r.func.__name__ in function_names]
        if self.args.monitor_lines and trigger != "render_all":
            func_name = file_and_line_to_def(self.filepath, self.line_number)
            matches = [r for r in _rs if r.func.__name__ == func_name]
            if len(matches) > 0:
                return matches
        return _rs

    async def render(self, trigger):
        renders = self.renderables(trigger)
        self.last_renders = renders
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
                for rp in render.passes(trigger):
                    result = await rp.run()
                    if trigger in ["initial", "render_storyboard", "resave"]:
                        self.preview.send(SVGPen.Composite(result, render.rect, viewBox=True), bg=render.bg, max_width=800)
                    if self.args.save_renders or trigger in ["render_all", "render_workarea"]:
                        did_render = True
                        prefix = self.args.file_prefix or render.prefix or self.filepath.stem
                        output_path = output_folder / f"{prefix}_{rp.suffix}.{self.args.format or render.fmt}"
                        rp.output_path = output_path
                        output_path.parent.mkdir(exist_ok=True, parents=True)
                        self.rasterize(result, render, output_path)
                        print(">>> saved...", "~/" + str(output_path.relative_to(Path.home())))
                if did_render:
                    render.package(self.filepath, output_folder)
                    self.show_message("Done!")
        except:
            self.show_error()
    
    def rasterize(self, content, render, path):
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
            print("hello")
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
        print("exit>", self.exit_code)
        sys.exit(self.exit_code)

    async def start(self):
        should_halt = await self.before_start()
        if should_halt:
            print("SHOULD HALT")
            self.on_exit()
        else:
            await self.reload_and_render("render_all" if self.args.all else "initial")
            await self.on_start()
            if self.args.watch:
                loop = asyncio.get_running_loop()
                self.watch_file_changes()
                await asyncio.gather(self.listen_to_ws())
            else:
                self.on_exit()
    
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
        elif action == "render_workarea":
            await self.reload_and_render(action)
        elif action in ["step_storyboard_forward", "step_storyboard_backward"]:
            increment = 1 if action == "step_storyboard_forward" else -1
            for render in self.last_renders:
                if hasattr(render, "storyboard"):
                    for idx, fidx in enumerate(render.storyboard):
                        nidx = (fidx + increment) % render.duration
                        render.storyboard[idx] = nidx
                    self.preview.clear()
                    await self.render("render_storyboard")
    
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
            print(f">>> resave: {Path(event.src_path).relative_to(Path.home())}")
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

    def on_exit(self):
        #if self.args.watch:
        #    print(f"<EXIT RENDERER ({exit_code})>")
        self.stop_watching_file_changes()
        self.preview.close()

def main():
    pargs, parser = Renderer.Argparser()
    Renderer(parser).main()

if __name__ == "__main__":
    main()