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


parser = argparse.ArgumentParser(prog="animation", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("file", type=str)
args = parser.parse_args()

filepath = Path(args.file).expanduser().resolve()
program = run_path(str(filepath))

preview = PersistentPreview()
preview.clear()

tests = program["tests"]
for test in tests:
    r = Rect(1920, 1080)
    result = test(r)
    preview.send(SVGPen.Composite(result, r, viewBox=True), bg=1, max_width=800)

preview.close()