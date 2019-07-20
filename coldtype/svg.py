import re
import os
import sys
import math
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.pens.transformPen import TransformPen
from fontTools.ufoLib.glifLib import Glyph
from fontTools.svgLib.path.parser import parse_path

if __name__ == "__main__":    
    import os
    import sys
    dirname = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(f"{dirname}/..")

from coldtype.geometry import Rect
from coldtype.ufo import GlyphStoreSetter
from coldtype.pens.datpen import DATPen


def read_svg_to_pen(file, gid, r=Rect((0, 0, 0, 100))):
    from bs4 import BeautifulSoup
    with open(file, "r") as f:
        soup = BeautifulSoup(f.read(), features="lxml")
        dp = DATPen()
        tp = TransformPen(dp, (1, 0, 0, -1, 0, r.h))
        for path in soup.find(id=gid).find_all("path"):
            parse_path(path.get("d"), tp)
        return dp

class SVGFileSetter(GlyphStoreSetter):
    def __init__(self, file):
        with open(os.path.expanduser(hs1), "r") as f:
            self.soup = BeautifulSoup(f.read(), features="lxml")
            self.capHeight = 750 # not
    
    def getGlyph(self, glyphName):
        return self.soup.find("glyph", {"glyph-name": glyphName})
    
    def getGlyphWidth(self, glyph):
        return float(glyph.get("horiz-adv-x"))
    
    def drawGlyphToPen(self, glyph, pen):
        parse_path(glyph.get("d"), pen)


if __name__ == "__main__":
    from bs4 import BeautifulSoup
    from coldtype.viewer import previewer
    from coldtype.pens.svgpen import SVGPen
    from coldtype.pens.axidrawpen import AxiDrawPen
    from random import randint

    hs1 = "~/Type/typeworld/hershey-text/hershey-text/svg_fonts/HersheyScript1.svg"
    sf = SVGFileSetter(hs1)

    #with previewer() as p:
    r = Rect(0,0,1100,850)
    dp = sf.getLine("G o o d h e r t z", leavePathsOpen=False).scale(0.2).attr(fill=None, stroke=0, strokeWidth=1).align(r)
        #dp = hs1f.getGlyph("B").attr(fill=None, stroke=0).scale(0.25).align(r)
        #dp.value = dp.value[:-1]
        #dp = DATPen()
        #dp.rect(r.inset(100, 100))
        #p.send(SVGPen.Composite([dp], r), r)
    ap = AxiDrawPen(dp, r)
    ap.draw(dry=0)