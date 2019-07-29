import os
import sys
import time

dirname = os.path.realpath(os.path.dirname(__file__))
if __name__ == "__main__":
    sys.path.append(f"{dirname}/../..")

from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from coldtype.geometry import Rect, Edge, Point
from coldtype.pens.svgpen import SVGPen
from coldtype.pens.datpen import DATPen
from coldtype.viewer import viewer

import math
try:
    from pyaxidraw import axidraw
except:
    pass

MOVE_DELAY = 0

class AxiDrawPen(BasePen):
    def __init__(self, dat, page):
        super().__init__(None)
        self.dat = dat
        self.page = page
        self.ad = None
        #dat.replay(self)
        self.last_moveTo = None
    
    def _moveTo(self, p):
        self.last_moveTo = p
        time.sleep(MOVE_DELAY)
        self.ad.moveto(*p)
        time.sleep(MOVE_DELAY)

    def _lineTo(self, p):
        self.ad.lineto(*p)

    def _curveToOne(self, p1, p2, p3):
        print("CANNOT CURVE")

    def _qCurveToOne(self, p1, p2):
        print("CANNOT CURVE")

    def _closePath(self):
        # can this work?
        if self.last_moveTo:
            self.ad.lineto(*self.last_moveTo)

    def draw(self, scale=0.01, dry=True, cm=False):
        if dry:
            with viewer() as v:
                dp = DATPen().record(self.dat).attr(fill=None, stroke=0)
                v.send(SVGPen.Composite([dp], self.page), self.page)
        else:
            self.dat.scale(scale)
            self.page = self.page.scale(scale)
            b = self.dat.bounds()
            limits = Rect(0, 0, 11, 8.5)
            if cm:
                limits = limits.scale(2.54)
            if b.x >= 0 and b.y >= 0 and b.w <= limits.w and b.h <= limits.h:
                print("Drawing!")
            else:
                print("Too big!", b)
                return False
            ad = axidraw.AxiDraw()
            ad.interactive()
            ad.options.units = 1 if cm else 0
            ad.options.speed_pendown = 110
            ad.options.speed_penup = 110

            ad.connect()
            ad.penup()
            self.ad = ad
            tp = TransformPen(self, (1, 0, 0, -1, 0, self.page.h))

            self.dat.replay(tp)
            time.sleep(MOVE_DELAY)
            ad.penup()
            ad.moveto(0,0)
            ad.disconnect()


if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath("."))
    from coldtype.viewer import viewer
    from coldtype.pens.datpen import DATPenSet
    from coldtype import Slug, Style
    #from coldtype.ufo import UFOStringSetter
    from random import random, randint
    from string import ascii_lowercase, ascii_uppercase
 
    def text_test():
        ff = "~/Type/typeworld/hershey_ufos_open_paths/Hershey-{:s}.ufo"
        r = Rect(0, 0, 1100, 850)
        strings = [
            #["The virtuosity of the cathode ray printer", "SimplexCartographicSans"],
            #["has been explored further", "SimplexCartographicScript"],
            #["with a number of", "DuplexPrincipalSans"],
            ["Butts", "TriplexGothicItalian"],
            #["digitalizations.", "TriplexGothicGerman"],
        ]
        rl = r.inset(0, 200)
        p = DATPen()
        #rows = r.inset(0, 100).subdivide(len(strings), "maxy")
        for idx, (s, f) in enumerate(strings):
            s = Slug(s, Style(ff.format(f), 200, varyFontSize=1)).fit(500)
            rt, rl = rl.divide(s.strings[0].fontSize + 10, "maxy")
            s.pen().align(rt).replay(p)
        
        #for c in ascii_uppercase[0:1]:
            #time.sleep(2)
        ap = AxiDrawPen(p, r)
        ap.draw(dry=0)
    
    text_test()