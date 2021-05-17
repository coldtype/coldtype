import math, sys, os, re
from pathlib import Path

from coldtype.text import *
from drafting.text.reader import Font
from coldtype.pens.datpen import DATPen, DATPens, DATPenSet, DP, DPS
from coldtype.pens.dattext import DATText
#from coldtype.pens.datimage import DATImage
from drafting.geometry import *
from drafting.color import *
from coldtype.renderable import *
from coldtype.helpers import loopidx, sibling, raw_ufo, ßhide, ßshow, cycle_idx, random_series, show_points, glyph_to_uni, uni_to_glyph, glyph_to_class, DefconFont
from coldtype.time import *
#from coldtype.renderer.state import RendererState, Keylayer

name = "coldtype"
__version__ = "0.3.4"

__sibling__ = lambda x: x # will be redefined contextually

def noop():
    return None