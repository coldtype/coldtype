#!/usr/bin/env python

import sys
import os

dirname = os.path.dirname(__file__)
if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath(dirname + "/.."))

from coldtype.geometry import Rect
from coldtype.color import Color, normalize_color
from coldtype.animation import *
from coldtype.pens.svgpen import SVGPen
from coldtype.pens.cairopen import CairoPen
from coldtype.pens.drawbotpen import DrawBotPen
from coldtype.viewer import WebSocket, PersistentPreview, WEBSOCKET_ADDR, viewer
from coldtype import DATPen, DATPenSet, StyledString, Style, Lockup, T2L, Slug, Graf, GrafStyle

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from subprocess import Popen, PIPE, call
from runpy import run_path
import threading
import traceback
import websocket
import time

from random import random, randint, seed
import math
import json
import pathlib
import argparse
import re
from pathlib import Path

parser = argparse.ArgumentParser(prog="animation", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("file", type=str)
parser.add_argument("-s", "--slice", type=str, default=None)
parser.add_argument("-pss", "--prevent-sub-slicing", action="store_true", default=False)
parser.add_argument("-isp", "--is-subprocess", action="store_true", default=False)
parser.add_argument("-ns", "--no-sound", action="store_true", default=False)
parser.add_argument("-rw", "--renderworkareas", action="store_true", default=False)
parser.add_argument("-a", "--all", action="store_true", default=False)
parser.add_argument("-w", "--watch", action="store_true", default=False)
parser.add_argument("-l", "--layers", type=str, default=None)
parser.add_argument("-r", "--rasterizer", type=str, default="drawbot")
parser.add_argument("-i", "--icns", action="store_true", default=False)
args = parser.parse_args()

filepath = None
anm = None
program = None

running_renderers = []

class LayerException(Exception):
    pass


def reload_animation():
    global filepath
    global anm
    try:
        program = run_path(str(filepath))
    except Exception as e:
        print(">>> CAUGHT")
        print(traceback.format_exc())
        with viewer() as vwr:
            vwr.send(f"<pre>{traceback.format_exc()}</pre>", None)
        return None
    if "animation" in program:
        anm = program["animation"]
    elif "render" in program:
        anm = Animation(program["render"])
    else:
        print(">>> no animation or render function found <<<")
        return None
    return anm

filepath = pathlib.Path(args.file).expanduser().resolve()
anm = None
reload_animation()


def read_layers(anm):
    layers = anm.layers
    if args.layers:
        layers = [l.strip() for l in args.layers.split(",")]
        for l in layers:
            if not anm.layers or l not in anm.layers:
                raise LayerException(f"No layer named {l}")
    return layers


def get_frames_folders(anm):
    frames_folder = filepath.parent.joinpath(f"{filepath.stem}_frames")
    frames_folder.mkdir(exist_ok=True)
    all_layers_folder = None
    if anm.layers:
        all_layers_folder = filepath.parent.joinpath(f"{filepath.stem}_layers")
        all_layers_folder.mkdir(exist_ok=True)
        for layer_name in anm.layers:
            layer_frames_folder = all_layers_folder.joinpath(f"{filepath.stem}_{layer_name}_frames")
            layer_frames_folder.mkdir(exist_ok=True)
    return frames_folder, all_layers_folder


def render_iconset():
    # inspired by https://retifrav.github.io/blog/2018/10/09/macos-convert-png-to-icns/
    global filepath
    anm = reload_animation()
    layers = read_layers(anm)
    frames_folder, all_layers_folder = get_frames_folders(anm)
    iconset = filepath.parent.joinpath(filepath.stem + ".iconset")
    iconset.mkdir(parents=True, exist_ok=True)

    d = 1024
    while d >= 16:
        aframe = render_frame(anm, layers, frames_folder, None, 0, d, flatten=True, manual=True)
        print(aframe.filepath)
        for x in [1, 2]:
            if x == 2 and d == 16:
                continue
            if x == 1:
                fn = f"icon_{d}x{d}.png"
            elif x == 2:
                fn = f"icon_{int(d/2)}x{int(d/2)}@2x.png"
            call(["sips", "-z", str(d), str(d), str(aframe.filepath), "--out", str(iconset.joinpath(fn))])
        d = int(d/2)
    
    call(["iconutil", "-c", "icns", str(iconset)])


def render_frame(anm,
        layers, folder, layers_folder, doneness, i,
        flatten=False,
        manual=False):
    frame_start_time = time.time()
    if i < 0:
        return
    if not manual and i >= anm.timeline.duration:
        return
    frame_path = folder.joinpath("{:s}_{:04d}.png".format(filepath.stem, i))
    aframe = AnimationFrame(i, anm, frame_path, layers or [])
    result = anm.render(aframe)
    rendered = False
    if layers:
        if not result:
            result = {}
        if not isinstance(result, dict):
            raise LayerException("When rendering layers, render func must return dict")

        if flatten:
            rendered = False
            for layer_name, layer_pens in result.items():
                pens.extend(layer_pens)
            result = pens
        else:
            rendered = True        
            for layer_name in layers:
                layer_pens = result.get(layer_name, [])
                layer_frames_folder = layers_folder.joinpath(f"{filepath.stem}_{layer_name}_frames")
                layer_file = "{:s}_{:s}_{:04d}.png".format(filepath.stem, layer_name, i)
                layer_frame_path = layer_frames_folder.joinpath(layer_file)
                DrawBotPen.Composite(layer_pens, anm.rect, str(layer_frame_path), scale=1)
                elapsed = time.time() - frame_start_time
                print(layer_frame_path.name, "({:0.2f}s) [{:04.1f}%]".format(elapsed, doneness))
    if not rendered:
        if not result:
            result = []
        if args.rasterizer == "drawbot":
            DrawBotPen.Composite(result, anm.rect, str(frame_path), scale=1)
        else:
            CairoPen.Composite(result, anm.rect, str(frame_path))#, scale=1)
        elapsed = time.time() - frame_start_time
        print(aframe.filepath.name, "({:0.2f}s) [{:04.1f}%]".format(elapsed, doneness))
    return aframe


def render_subslice(anm, layers, folder, layers_folder, frames):
    lf = len(frames)
    for idx, i in enumerate(frames):
        doneness =  idx / lf * 100
        render_frame(anm, layers, folder, layers_folder, doneness, i)


def render_slice(frames):
    global anm

    layers = read_layers(anm)
    layers_arg = ",".join(layers or [])

    start = time.time()
    frames_folder, all_layers_folder = get_frames_folders(anm)
    
    if args.is_subprocess or args.prevent_sub_slicing or len(frames) < 10:
        render_subslice(anm, layers, frames_folder, all_layers_folder, frames)
    else:
        group = math.floor(len(frames) / 8)
        threads = []
        f = frames[0]
        subslices = []
        while f <= frames[-1]:
            nf = min(f + group, frames[-1]+1)
            subslice = list(range(f, nf))
            subslices.append(subslice)
            f = nf
        
        global running_renderers
        for r in running_renderers:
            if r:
                r.terminate()
        
        running_renderers = []
        completed_renderers = []

        if 0 not in frames:
            # need to do this to trigger a filesystem-change detection in premiere
            render_subslice(anm, layers, frames_folder, all_layers_folder, [0, anm.timeline.duration-1])

        for subslice in subslices:
            print(subslice[:1])
            sargs = [
                "python",
                __file__,
                args.file,
                "-s", f"{subslice[0]}:{subslice[-1]+1}",
                "-isp",
                "-l", layers_arg
            ]
            if args.no_sound:
                sargs.append("-ns")
            renderer = Popen(sargs)
            running_renderers.append(renderer)
        
        while running_renderers.count(None) != len(running_renderers):
            for idx, renderer in enumerate(running_renderers):
                if renderer:
                    retcode = renderer.poll()
                    if retcode == 5:
                        running_renderers[idx] = None
            time.sleep(.1)

    if args.is_subprocess:
        if args.no_sound:
            pass
        else:
            os.system("afplay /System/Library/Sounds/Pop.aiff")
        sys.exit(5)
    else:
        print("TIME >>>", time.time() - start)
        if args.no_sound:
            pass
        else:
            os.system("afplay /System/Library/Sounds/Frog.aiff")


def preview_storyboard():
    layers = read_layers(anm)
    with viewer() as vwr:
        #buttons = """
        #<button onclick="websocket.send('rw')">rw</button>
        #<button onclick="websocket.send('all')">all</button>
        #"""
        #vwr.send(buttons)
        for frame in anm.timeline.storyboard:
            print(">>> PREVIEW", frame)
            aframe = AnimationFrame(frame, anm, None, layers)
            try:
                result = anm.render(aframe)
                if not result:
                    result = []
                if isinstance(result, dict):
                    pens = []
                    for layer_name, layer_pens in result.items():
                        pens.extend(layer_pens)
                    result = pens
                vwr.send(SVGPen.Composite(result, anm.rect, viewBox=True), bg=anm.bg, max_width=800)
            except Exception as e:
                print(traceback.format_exc())
                vwr.send(f"<pre>{traceback.format_exc()}</pre>", None)


def render(frames_fn=None):
    anm = reload_animation()
    if anm:
        preview_storyboard()
        if frames_fn:
            frames = frames_fn(anm)
            render_slice(frames)


def workarea_frames(anm):
    frames = []
    for wa in anm.timeline.workareas:
        frames.extend(list(wa))
    return frames


def all_frames(anm):
    return list(range(0, anm.timeline.duration+1))


class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        global anm
        p = event.src_path
        if p in anm.watches:
            print("save>>>", os.path.basename(p))
            render()
        elif p.endswith("f13.txt") or p.endswith(".py"): #or p.endswith("Auto-Save"):
            print("save>>>", os.path.basename(p))
            render()
        elif p.endswith("f14.txt"):
            render(workarea_frames)
        elif p.endswith("f15.txt"):
            render(all_frames)
        else:
            pass

def on_message(ws, message):
    if message == "rw":
        render(workarea_frames)
    elif message == "all":
        render(all_frames)

def watch_changes():
    rand_file = Path("~/signals").expanduser().resolve()
    render()
    handler = Handler()
    observer = Observer()
    observer2 = Observer()
    print("... watching ...")
    observer.schedule(handler, path=str(filepath.parent), recursive=True)
    observer2.schedule(handler, path=str(rand_file), recursive=True)
    observer.start()
    observer2.start()
    #websocket.enableTrace(True) # necessary?
    # https://github.com/websocket-client/websocket-client#examples
    ws = websocket.WebSocketApp(WEBSOCKET_ADDR, on_message=on_message)
    ws.run_forever()
    observer.stop()
    observer.join()
    observer2.stop()
    observer2.join()

def read_slice(slice_str):
    sl = slice(*map(lambda x: int(x.strip()) if x.strip() else None, slice_str.split(':')))
    return list(range(*sl.indices(100000)))


if args.icns:
    render_iconset()
elif args.watch:
    watch_changes()
elif args.renderworkareas:
    render(workarea_frames)
elif args.all:
    render(all_frames)
elif args.slice:
    render_slice(read_slice(args.slice))
else:
    render()

for r in running_renderers:
    if r:
        r.terminate()