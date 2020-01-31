#!/usr/bin/env python

import sys, os, re, json, math
from pathlib import Path

import coldtype
import coldtype.animation
from coldtype.geometry import Rect
from coldtype.color import Color, normalize_color
from coldtype.animation import *
from coldtype.pens.svgpen import SVGPen
from coldtype.pens.cairopen import CairoPen
from coldtype.pens.drawbotpen import DrawBotPen
from coldtype.viewer import WebSocket, PersistentPreview, WEBSOCKET_ADDR
#from coldtype import DATPen, DATPenSet, StyledString, Style, Lockup, T2L, Slug, Graf, GrafStyle

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from subprocess import Popen, PIPE, call
from random import random, randint, seed
from runpy import run_path
import threading
import traceback
import websocket
import time

from inspect import getframeinfo, stack

def debuginfo():
    caller = getframeinfo(stack()[2][0])
    print(">>>>> %s:%d" % (caller.filename, caller.lineno))

import argparse
import importlib

parser = argparse.ArgumentParser(prog="animation", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("file", type=str)
parser.add_argument("-s", "--slice", type=str, default=None)
parser.add_argument("-dss", "--do-sub-slicing", action="store_true", default=False)
parser.add_argument("-isp", "--is-subprocess", action="store_true", default=False)
parser.add_argument("-ns", "--no-sound", action="store_true", default=False)
parser.add_argument("-rw", "--renderworkareas", action="store_true", default=False)
parser.add_argument("-a", "--all", action="store_true", default=False)
parser.add_argument("-w", "--watch", action="store_true", default=False)
parser.add_argument("-l", "--layers", type=str, default=None)
parser.add_argument("-pl", "--preview-layers", type=str, default=None)
parser.add_argument("-f", "--format", type=str, default="png")
parser.add_argument("-cfn", "--custom-filename", type=str, default=None)
parser.add_argument("-r", "--rasterizer", type=str, default="drawbot")
parser.add_argument("-i", "--icns", action="store_true", default=False)
parser.add_argument("-arc", "--always-reload-coldtype", action="store_true", default=False)
parser.add_argument("-wsi", "--write-storyboard-images", action="store_true", default=False)
parser.add_argument("-rfa", '--read-from-adobe', action='store_true', default=False)
args = parser.parse_args()

filepath = None
anm = None
original_layers = None
program = None
preview = PersistentPreview()

running_renderers = []

class LayerException(Exception):
    pass


def read_layers(anm):
    layers = anm.layers
    if args.layers:
        layers = [l.strip() for l in args.layers.split(",")]
        for l in layers:
            if not anm.layers or l not in anm.layers:
                raise LayerException(f"(render) No layer named {l}")
    return layers


def read_preview_layers(anm):
    global original_layers
    render_layers = read_layers(anm)

    additional_preview_layers = []
    if args.preview_layers:
        players = [l.strip() for l in args.preview_layers.split(",")]
        for l in players:
            if l not in original_layers:
                raise LayerException(f"(preview) No layer named {l}")
            elif l not in render_layers:
                additional_preview_layers.append(l)
    
    preview_layers = []
    for l in original_layers:
        if l in render_layers or l in additional_preview_layers:
            preview_layers.append(l)

    return preview_layers


def reload_animation():
    if args.always_reload_coldtype:
        try:
            importlib.reload(coldtype.animation.premiere)
            importlib.reload(coldtype.pens.datpen)
            importlib.reload(coldtype.text.reader)
            importlib.reload(coldtype.text.composer)
            importlib.reload(coldtype.text)
            importlib.reload(coldtype.animation)
            importlib.reload(coldtype)
            
        except Exception as e:
            print(">>> CAUGHT COLDTYPE")
            print(traceback.format_exc())
            preview.send(f"<pre>{traceback.format_exc()}</pre>", None)
            return None
    global filepath
    global anm
    try:
        program = run_path(str(filepath))
    except Exception as e:
        print(">>> CAUGHT")
        print(traceback.format_exc())
        preview.send(f"<pre>{traceback.format_exc()}</pre>", None)
        return None
    if "animation" in program:
        anm = program["animation"]
    elif "render" in program:
        anm = Animation(program["render"])
    else:
        print(">>> no animation or render function found <<<")
        return None
    anm.sourcefile = filepath
    global original_layers
    original_layers = anm.layers.copy()
    anm.layers = read_layers(anm)

    if not anm.format and args.format:
        anm.format = args.format
    return anm

filepath = Path(args.file).expanduser().resolve()
anm = None
reload_animation()


def get_frames_folder(anm, mkdir=True):
    layers_folder = filepath.parent.joinpath(f"{filepath.stem}_layers")
    if mkdir:
        layers_folder.mkdir(exist_ok=True)
    for layer_name in anm.layers:
        layer_frames_folder = layers_folder.joinpath(f"{filepath.stem}_{layer_name}_frames")
        if mkdir:
            layer_frames_folder.mkdir(exist_ok=True)
    return layers_folder


def render_iconset():
    # inspired by https://retifrav.github.io/blog/2018/10/09/macos-convert-png-to-icns/
    global filepath
    anm = reload_animation()
    layers = read_layers(anm)
    layers_folder = get_frames_folder(anm)
    iconset = filepath.parent.joinpath(filepath.stem + ".iconset")
    iconset.mkdir(parents=True, exist_ok=True)

    d = 1024
    while d >= 16:
        aframe, result = render_frame(anm, layers, layers_folder, 0, d, manual=True)
        print(aframe.filepaths["main"])
        for x in [1, 2]:
            if x == 2 and d == 16:
                continue
            if x == 1:
                fn = f"icon_{d}x{d}.png"
            elif x == 2:
                fn = f"icon_{int(d/2)}x{int(d/2)}@2x.png"
            call(["sips", "-z", str(d), str(d), str(aframe.filepaths["main"]), "--out", str(iconset.joinpath(fn))])
        d = int(d/2)
    
    call(["iconutil", "-c", "icns", str(iconset)])


def render_frame(
        anm,
        layers,
        layers_folder,
        doneness,
        i,
        #flatten=False,
        manual=False,
        write_to_disk=True,
    ):
    frame_start_time = time.time()
    if i < 0:
        return None, None
    if not manual and i >= anm.timeline.duration:
        return None, None
    
    aframe = AnimationFrame(i, anm, layers)
    result = anm.render(aframe)
    
    if not result:
        result = {}
    if not isinstance(result, dict):
        result = {"main": result}
    
    for layer_name in layers:
        layer_pens = result.get(layer_name, [])
        if hasattr(layer_pens, "filmjitter"):
            layer_pens = [layer_pens]
            result[layer_name] = layer_pens
        layer_frames_folder = layers_folder.joinpath(f"{filepath.stem}_{layer_name}_frames")
        if anm.filename:
            layer_file = "{:s}.{}".format(anm.filename(aframe), anm.format)
        elif args.custom_filename:
            layer_file = "{:s}.{}".format(args.custom_filename, anm.format)
        else:
            layer_file = "{:s}_{:s}_{:04d}.{}".format(filepath.stem, layer_name, i, anm.format)
        layer_frame_path = layer_frames_folder.joinpath(layer_file)
        aframe.filepaths[layer_name] = layer_frame_path
        if write_to_disk:
            if args.rasterizer == "drawbot":
                DrawBotPen.Composite(layer_pens, anm.rect, str(layer_frame_path), scale=1)
            else:
                CairoPen.Composite(layer_pens, anm.rect, str(layer_frame_path))#, scale=1)
            elapsed = time.time() - frame_start_time
            print(layer_frame_path.name, "({:0.2f}s) [{:04.1f}%]".format(elapsed, doneness))
    
    return aframe, result


def render_subslice(anm, layers, layers_folder, frames):
    lf = len(frames)
    for idx, i in enumerate(frames):
        doneness =  idx / lf * 100
        render_frame(anm, layers, layers_folder, doneness, i)


def render_slice(frames):
    global anm

    layers = read_layers(anm)
    layers_arg = ",".join(layers or [])

    start = time.time()
    layers_folder = get_frames_folder(anm)
    
    if not args.do_sub_slicing:
        if 0 not in frames:
            frames.insert(0, 0)
        render_subslice(anm, layers, layers_folder, frames)
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
            render_subslice(anm, layers, layers_folder, [0, anm.timeline.duration-1])

        for subslice in subslices:
            print(subslice[:1])
            sargs = [
                sys.executable,
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
    preview_layers = read_preview_layers(anm)
    layers_folder = get_frames_folder(anm, mkdir=args.write_storyboard_images)
    preview.clear()

    anm.layers = preview_layers

    for frame in anm.timeline.storyboard:
        try:
            print("------------------------------------------------------------")
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PREVIEW {:04d}".format(frame))
            aframe, result = render_frame(anm, preview_layers, layers_folder, 0, frame, write_to_disk=args.write_storyboard_images, manual=1)
            pens = []
            for layer_name, layer_pens in result.items():
                pens.extend(layer_pens)
            preview.send(SVGPen.Composite(pens, anm.rect, viewBox=True), bg=anm.bg, max_width=800)
        except Exception as e:
            print(traceback.format_exc())
            preview.send(f"<pre>{traceback.format_exc()}</pre>", None)
    
    anm.layers = layers


def render(frames_fn=None):
    #debuginfo()
    rendered_frames = False
    anm = reload_animation()
    if anm:
        preview_storyboard()
        if frames_fn:
            rendered_frames = True
            frames = frames_fn(anm)
            render_slice(frames)
        if not rendered_frames and args.write_storyboard_images:
            # always need to render 0 to trigger cache-bust in adobe products
            layers = read_layers(anm)
            layers_folder = get_frames_folder(anm)
            render_frame(anm, layers, layers_folder, 0, 0)
            rendered_frames = True
        if rendered_frames:
            preview.send(json.dumps(dict(rendered=True, prefix=anm.sourcefile.stem, fps=anm.timeline.fps)), full=True)

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
        external_timeline = args.read_from_adobe and hasattr(anm.timeline, "currentWorkarea")

        #def request_serialization(action):
        #    preview.send(json.dumps(dict(serialization_request=True, prefix=anm.sourcefile.stem, action=action)), full=True)
        
        #def send_edit_action(action):
        #    preview.send(json.dumps(dict(edit_action=True, prefix=anm.sourcefile.stem, action=action)), full=True)

        if p in anm.watches or p.endswith(".py"):
            print("save>>>", os.path.basename(p))
            #if external_timeline:
            #    request_serialization("render_storyboard")
            #else:
            render()
        #elif p.endswith("render-workarea.txt"):
        #    if external_timeline:
        #        request_serialization("render_workarea")
        #    else:
        #        render(workarea_frames)
        #elif p.endswith("render-all.txt"):
        #    if external_timeline:
        #        request_serialization("render_all")
        #    else:
        #        render(all_frames)
        #elif p.endswith("select-workarea.txt"):
        #    request_serialization("select_workarea")
        #elif p.endswith("split-word-at-playhead.txt"):
        #    send_edit_action("split_word_at_playhead")
        #elif p.endswith("newline.txt"):
        #    send_edit_action("newline")
        #elif p.endswith("newsection.txt"):
        #    send_edit_action("newsection")
        #elif p.endswith("capitalize.txt"):
        #    send_edit_action("capitalize")
        else:
            pass

def request_serialization(action):
    global anm
    preview.send(json.dumps(dict(serialization_request=True, prefix=anm.sourcefile.stem, action=action)), full=True)

def send_edit_action(action):
    global anm
    preview.send(json.dumps(dict(edit_action=True, prefix=anm.sourcefile.stem, action=action)), full=True)

def on_message(ws, message):
    try:
        jdata = json.loads(message)
        action = jdata.get("action")
        if jdata.get("serialization"):
            print("yes here")
            if action == "select_workarea":
                anm = reload_animation()
                cw = anm.timeline.currentWorkarea()
                if cw:
                    start, end = cw
                    preview.send(json.dumps(dict(workarea_update=True, prefix=anm.sourcefile.stem, fps=anm.timeline.fps, start=start, end=end)), full=True)
                else:
                    print("No CTI/trackGroups found")
            elif action == "render_workarea":
                render(workarea_frames)
            elif action == "render_all":
                render(all_frames)
            else:
                render()
        elif jdata.get("trigger_from_app"):
            if action in [
                "render_storyboard",
                "render_workarea",
                "render_all"
            ]:
                if action == "render_storyboard":
                    render()
                elif action == "render_workarea":
                    render(workarea_frames)
                elif action == "render_all":
                    render(all_frames)
            elif action in [
                "select_workarea",
                "newsection",
                "newline",
                "split_word_at_playhead",
                "capitalize",
            ]:
                if action == "select_workarea":
                    request_serialization(action)
                else:
                    send_edit_action(action)

            print("TRIGGER>>>>>>>>>>>", action)
    except:
        if message == "rw":
            render(workarea_frames)
        elif message == "all":
            render(all_frames)
        else:
            pass
            #print(">>>>>>>>>>>>>>>>>>>>>>>>>>", message)

def watch_changes():
    global anm
    to_watch = set([
        filepath.parent,
    ])
    for w in anm.watches:
        to_watch.add(w.parent)
    if args.always_reload_coldtype:
        to_watch.add(Path(__file__).parent.joinpath("coldtype"))
    render()
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

preview.close()
for r in running_renderers:
    if r:
        r.terminate()