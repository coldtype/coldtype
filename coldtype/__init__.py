import math
import sys
import os
import re
import copy
from pathlib import Path

name = "coldtype"
__version__ = "0.0.1"

from coldtype.text import *
from coldtype.text.reader import Font
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.geometry import Rect
from coldtype.color import Color, Gradient, normalize_color
from defcon import Font as DefconFont

def raw_ufo(path):
    return DefconFont(normalize_font_path(path))

def renderable(func):
    func.renderable = True
    return func