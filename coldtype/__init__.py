import math
import sys
import os
import re
import copy

name = "coldtype"

from coldtype.text import *
from coldtype.text.reader import Font
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.geometry import Rect

def renderable(func):
    func.renderable = True
    return func