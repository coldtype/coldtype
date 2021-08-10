import math, sys, os, re
from pathlib import Path

from coldtype.text import *
from coldtype.text.reader import Font
from coldtype.pens.datpen import DATPen, DATPens, DATPenSet, DP, DPS, P, PS
from coldtype.pens.dattext import DATText
from coldtype.geometry import *
from coldtype.color import *
from coldtype.renderable import *
from coldtype.helpers import loopidx, sibling, raw_ufo, ßhide, ßshow, cycle_idx, random_series, show_points, glyph_to_uni, uni_to_glyph, glyph_to_class, DefconFont
from coldtype.time import *
from coldtype.img.blendmode import BlendMode
from coldtype.grid import Grid

name = "coldtype"
__version__ = "0.5.18"

__sibling__ = lambda x: x # will be redefined contextually
#λ = None

def debug_txt(r, txt, font_size=42, **kwargs):
    return DATText(txt, Style("Times", font_size, load_font=0, **kwargs), r.inset(20))

def noop():
    return None