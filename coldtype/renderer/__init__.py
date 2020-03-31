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

import coldtype
from coldtype.geometry import Rect
from coldtype.pens.svgpen import SVGPen
from coldtype.pens.cairopen import CairoPen
from coldtype.pens.drawbotpen import DrawBotPen
from coldtype.viewer import PersistentPreview, WEBSOCKET_ADDR


class Renderer():
    def Argparser(name="coldtype-render"):
        parser = argparse.ArgumentParser(prog="coldtype-render", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("file", type=str)
        parser.add_argument("-w", "--watch", action="store_true", default=False)
        return parser

    def __init__(self, parser):
        self.args = parser.parse_args()
        self.filepath = Path(self.args.file).expanduser().resolve()
        self.preview = PersistentPreview()
        self.preview.clear()
        self.program = None

        self.watchees = [self.filepath]
        self.observers = []

        signal.signal(signal.SIGINT, self.on_exit_signal)

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
                    if v.path not in self.watchees:
                        self.watchees.append(v.path)
                    for ext in v.font.getExternalFiles():
                        if ext not in self.watchees:
                            self.watchees.append(ext)
        except Exception as e:
            self.program = None
            self.show_error()

    async def render(self, trigger):
        page = self.program["page"]
        renders = self.program["renders"]
        render_data = self.program.get("render_data", {})
        try:
            for render in renders:
                if inspect.iscoroutinefunction(render):
                    result = await render()
                else:
                    result = render()
                self.preview.send(SVGPen.Composite(result, page, viewBox=True), bg=render_data.get("bg", 1), max_width=800)
        except:
            self.show_error()
    
    async def reload_and_render(self, trigger):
        wl = len(self.watchees)
        self.preview.clear()
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
        jdata = json.loads(message)
        await self.on_message(jdata, jdata.get("action"))

    async def listen_to_ws(self):
        async with websockets.connect(WEBSOCKET_ADDR) as websocket:
            async for message in websocket:
                await self.process_ws_message(message)
    
    async def on_modified(self, event):
        if Path(event.src_path) in self.watchees:
            print(f">>>>>>>> resave ({Path(event.src_path).name})")
            await self.reload_and_render("resave")

    def watch_file_changes(self):
        self.observers = []
        dirs = set([w.parent for w in self.watchees])
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