import math, sys, os, re
from pathlib import Path

# source: https://github.com/PixarAnimationStudios/USD/issues/1372

def monkeypatch_ctypes():
    import ctypes.util, platform
    uname = os.uname()
    if uname.sysname == "Darwin" and uname.release >= "20.":
        real_find_library = ctypes.util.find_library
        def find_library(name):
            if name in {"OpenGL", "GLUT"}:  # add more names here if necessary
                return f"/System/Library/Frameworks/{name}.framework/{name}"
            elif name in {"freetype"}:
                res = real_find_library(name)
                if res.startswith("/usr/local") and platform.processor() == "arm":
                    return "/opt/homebrew/lib/libfreetype.dylib"
            return real_find_library(name)
        ctypes.util.find_library = find_library
    return

monkeypatch_ctypes()

from coldtype.text import *
from coldtype.text.reader import Font
from coldtype.drawing import Drawing
from coldtype.geometry import *
from coldtype.color import *
from coldtype.renderable import *
from coldtype.renderer.reader import Programs
from coldtype.helpers import loopidx, sibling, raw_ufo, ßhide, ßshow, cycle_idx, random_series, glyph_to_uni, uni_to_glyph, glyph_to_class, DefconFont
from coldtype.time import *
from coldtype.time.easing import ez
from coldtype.time.nle.ascii import AsciiTimeline
from coldtype.time.midi import MidiTimeline
from coldtype.img.blendmode import BlendMode
from coldtype.grid import Grid

name = "coldtype"
__version__ = "0.8.1"

__FILE__ = None # will be redefined contextually
__BLENDER__ = None # will be redefined contextually

__sibling__ = lambda x: x # will be redefined contextually
__inputs__ = [] # will be redefined contextually
__memory__ = [] # will be redefined contextually
__as_config__ = False # will be redefined contextually
λ = None
ι = None
ℛ = lambda x: x

ß = Drawing
P = Drawing
PS = Drawing

# temporary aliases for backwards compat
DATPens = Drawing
DATPen = Drawing
DPS = Drawing
DP = Drawing

def debug_txt(r, txt, font_size=42, **kwargs):
    return Drawing().text(txt,
        Style("Times", font_size, load_font=0, **kwargs),
        r.inset(20))

def noop():
    return None