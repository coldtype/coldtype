#!/usr/bin/env python

import sys, os, re, json, math
from pathlib import Path

import argparse
import importlib
from runpy import run_path

import asyncio
import signal
import websockets
from watchgod import awatch, Change

import coldtype
from coldtype import FontGoggle
from coldtype.geometry import Rect
from coldtype.pens.svgpen import SVGPen
from coldtype.pens.cairopen import CairoPen
from coldtype.pens.drawbotpen import DrawBotPen
from coldtype.viewer import PersistentPreview, WEBSOCKET_ADDR

import traceback
from subprocess import call


parser = argparse.ArgumentParser(prog="coldtype-render", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("file", type=str)
parser.add_argument("-w", "--watch", action="store_true", default=False)
parser.add_argument("-i", "--icns", action="store_true", default=False)
args = parser.parse_args()

filepath = Path(args.file).expanduser().resolve()

preview = PersistentPreview()
preview.clear()


def reload_file():
    #importlib.reload(coldtype.text.reader)
    #importlib.reload(coldtype)
    program = run_path(str(filepath))
    return program

def show_error():
    print(">>> CAUGHT COLDTYPE")
    print(traceback.format_exc())
    preview.send(f"<pre>{traceback.format_exc()}</pre>", None)

async def reload_and_render():
    try:
        program = reload_file()
    except Exception as e:
        show_error()
        return None
    
    page = program["page"]
    renders = program["renders"]
    preview.clear()
    #for k, v in program.items():
    #    if isinstance(v, coldtype.text.reader.FontGoggle):
    #        await v.load()
    try:
        for render in renders:
            result = await render()
            preview.send(SVGPen.Composite(result, page, viewBox=True), bg=1, max_width=800)
    except:
        show_error()
    return program


async def render_iconset():
    # inspired by https://retifrav.github.io/blog/2018/10/09/macos-convert-png-to-icns/
    program = await reload_and_render()
    page = program["page"]
    render_fn = program["render_icon"]
    
    iconset_source = filepath.parent.joinpath(filepath.stem + "_source")
    iconset_source.mkdir(parents=True, exist_ok=True)
    iconset = filepath.parent.joinpath(filepath.stem + ".iconset")
    iconset.mkdir(parents=True, exist_ok=True)

    d = 1024
    while d >= 16:
        result = render_fn(d)
        path = iconset_source.joinpath(f"source_{d}.png")
        DrawBotPen.Composite(result, page, str(path), scale=1)
        for x in [1, 2]:
            if x == 2 and d == 16:
                continue
            if x == 1:
                fn = f"icon_{d}x{d}.png"
            elif x == 2:
                fn = f"icon_{int(d/2)}x{int(d/2)}@2x.png"
            call(["sips", "-z", str(d), str(d), str(path), "--out", str(iconset.joinpath(fn))])
        d = int(d/2)
    
    call(["iconutil", "-c", "icns", str(iconset)])

async def consumer(message):
    try:
        if json.loads(message).get("action") == "render_storyboard":
            await reload_and_render()
    except:
        pass

async def listen_to_ws():
    async with websockets.connect(WEBSOCKET_ADDR) as websocket:
        async for message in websocket:
            await consumer(message)

async def watch_file_changes():
   async for changes in awatch(filepath.parent):
       for change, path in changes:
           if change == Change.modified:
               print(change, path)
               await reload_and_render()

def on_exit(frame, signal):
    print("<EXIT>")
    preview.close()
    asyncio.get_event_loop().stop()
    sys.exit(0)

signal.signal(signal.SIGINT, on_exit)

async def main():
    await asyncio.gather(
        listen_to_ws(),
        watch_file_changes(),
    )

if args.icns:
    asyncio.get_event_loop().run_until_complete(render_iconset())
else:
    asyncio.get_event_loop().run_until_complete(reload_and_render())
    if args.watch:
        asyncio.run(main())