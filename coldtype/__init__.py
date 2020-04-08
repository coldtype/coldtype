import math, sys, os, re
from pathlib import Path
from defcon import Font as DefconFont

from coldtype.text import *
from coldtype.text.reader import Font
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.geometry import *
from coldtype.color import *
from coldtype.renderable import *
from coldtype.helpers import *
from coldtype.animation import *

name = "coldtype"
__version__ = "0.0.1"

def raw_ufo(path):
    return DefconFont(normalize_font_path(path))