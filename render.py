#!/usr/bin/env python

import sys, os, re, json, math
from pathlib import Path

import argparse
import importlib
from runpy import run_path

from coldtype.geometry import Rect
from coldtype.pens.svgpen import SVGPen
from coldtype.pens.cairopen import CairoPen
from coldtype.pens.drawbotpen import DrawBotPen
from coldtype.viewer import WebSocket, PersistentPreview, WEBSOCKET_ADDR

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import websocket

from subprocess import Popen, PIPE, call


parser = argparse.ArgumentParser(prog="coldtype-render", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("file", type=str)
parser.add_argument("-w", "--watch", action="store_true", default=False)
parser.add_argument("-i", "--icns", action="store_true", default=False)
args = parser.parse_args()

filepath = Path(args.file).expanduser().resolve()

preview = PersistentPreview()
preview.clear()


def reload_file():
    program = run_path(str(filepath))
    return program


def reload_and_render():
    program = reload_file()
    page = program["page"]
    renders = program["renders"]
    preview.clear()
    for render in renders:
        result = render()
        preview.send(SVGPen.Composite(result, page, viewBox=True), bg=1, max_width=800)
    return program


class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        p = event.src_path
        if p.endswith(".py"):
            print("save>>>", os.path.basename(p))
            reload_and_render()
        else:
            pass


def on_message(ws, message):
    try:
        print(">>>ws", message.strip()[:10])
    except:
        pass


def watch_changes():
    to_watch = set([
        filepath.parent,
    ])
    handler = Handler()
    print("... watching ...")
    observers = []
    for w in to_watch:
        o = Observer()
        o.schedule(handler, path=str(w), recursive=True)
        o.start()
        observers.append(o)
    #websocket.enableTrace(True) # necessary?
    # https://github.com/websocket-client/websocket-client#examples
    ws = websocket.WebSocketApp(WEBSOCKET_ADDR, on_message=on_message)
    ws.run_forever()
    for o in observers:
        o.stop()
        o.join()


def render_iconset():
    # inspired by https://retifrav.github.io/blog/2018/10/09/macos-convert-png-to-icns/
    program = reload_and_render()
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

if args.icns:
    render_iconset()
else:
    reload_and_render()
    if args.watch:
        watch_changes()

preview.close()