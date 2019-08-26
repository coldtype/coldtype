import os
import sys
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.realpath(dirname + "/.."))

from coldtype.geometry import Rect, Point
from coldtype import Slug, Style, Graf
from coldtype.viewer import previewer
from coldtype.pens.datpen import DATPen
from coldtype.pens.svgpen import SVGPen
from coldtype.color import Color


def save_artifact(filename, content=None):
    p = dirname + "/artifacts/" + filename
    if not content:
        try:
            from drawBot import saveImage
            saveImage(p)
        except:
            print("No drawBot found, cannot save context to image")
    else:
        with open(p, "w") as f:
            f.write(content)