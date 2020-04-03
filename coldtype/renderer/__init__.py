import sys, os
from pathlib import Path

import asyncio
import signal
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
from coldtype.geometry import Rect
from coldtype.pens.svgpen import SVGPen
from coldtype.pens.cairopen import CairoPen
from coldtype.pens.drawbotpen import DrawBotPen
from coldtype.viewer import PersistentPreview, WEBSOCKET_ADDR


class Watchable(Enum):
    Source = "Source"
    Font = "Font"
    Library = "Library"


class Renderer():
    def Argparser(name="coldtype-render"):
        parser = argparse.ArgumentParser(prog="coldtype-render", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("file", type=str)
        parser.add_argument("-w", "--watch", action="store_true", default=False)
        parser.add_argument("-s", "--scale", type=float, default=1.0)
        parser.add_argument("-r", "--rasterizer", type=str, default="drawbot")
        parser.add_argument("-sv", "--save-renders", action="store_true", default=False)
        parser.add_argument("-rl", "--reload-libraries", action="store_true", default=False)
        return parser

    def __init__(self, parser):
        self.args = parser.parse_args()
        self.filepath = Path(self.args.file).expanduser().resolve()
        self.preview = PersistentPreview()
        self.preview.clear()
        self.program = None

        self.watchees = [[Watchable.Source, self.filepath]]
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

        signal.signal(signal.SIGINT, self.on_exit_signal)

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
            if hasattr(v, "renderable"):
                _rs.append(v)
        return _rs

    async def render(self, trigger):
        page = self.program["page"]
        renders = self.program.get("renders")
        if renders and len(renders) > 0:
            renders = renders
        else:
            renders = self.renderables()
        render_data = self.program.get("render_data", {})
        try:
            for render in renders:
                if inspect.iscoroutinefunction(render):
                    result = await render()
                else:
                    result = render()
                self.preview.send(SVGPen.Composite(result, page, viewBox=True), bg=render_data.get("bg", 1), max_width=800)
                if self.args.save_renders:
                    output_path = self.filepath.parent / f"{self.filepath.stem}_{render.__name__}.png"
                    self.rasterize(result, page, output_path)
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
        asyncio.run(self.start())

    async def start(self):
        await self.before_start()
        await self.reload_and_render("initial")
        await self.on_start()
        if self.args.watch:
            self.watch_file_changes()
            await asyncio.gather(self.listen_to_ws())
        else:
            self.on_exit(0)
    
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
    
    async def process_ws_message(self, message):
        try:
            jdata = json.loads(message)
            await self.on_message(jdata, jdata.get("action"))
        except:
            print("Malformed message", message)

    async def listen_to_ws(self):
        async with websockets.connect(WEBSOCKET_ADDR) as websocket:
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
            #o.join()

    def on_exit_signal(self, frame, signal):
        self.on_exit(0)

    def on_exit(self, exit_code):
        print(f"<EXIT RENDERER ({exit_code})>")
        self.stop_watching_file_changes()
        self.preview.close()
        asyncio.get_event_loop().stop()
        sys.exit(exit_code)