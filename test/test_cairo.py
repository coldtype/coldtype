import os
import math
import cairo

from test_preamble import *
from furniture.geometry import Rect

from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen


class CairoPen(BasePen):

    def __init__(self, ctx=None):
        BasePen.__init__(self, None)
        self.ctx = ctx

    def _moveTo(self, p):
        self.ctx.move_to(p[0], p[1])

    def _lineTo(self, p):
        self.ctx.line_to(p[0], p[1])

    def _curveToOne(self, p1, p2, p3):
        self.ctx.curve_to(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])

    def _qCurveToOne(self, p1, p2):
        print("NOT SUPPORTED")
    # self.ctx.quad_to(*p1+p2)

    def _closePath(self):
        self.ctx.close_path()

    def flipped(self, h):
        tp = TransformPen(self, (1, 0, 0, -1, 0, h))
        return tp


def ss_test():
    from coldtype import StyledString
    from coldtype.pens.datpen import DATPen
    from furniture.viewer import previewer
    from random import random

    r = Rect((0, 0, 300, 300))
    dt = DATPen()
    # dt.rect(r.inset(20, 20).take(2, "centery"))

    ss = StyledString("ABC", font="¬/ObviouslyVariable.ttf", fontSize=300, variations=dict(wdth=1, wght=0, scale=True))
    ss.place(r.inset(20, 0))
    dt.record(ss.asRecording())

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, r.w, r.h)
    ctx = cairo.Context(surface)
    ctx.scale(1, 1)

    ctx.set_source_rgb(1, 1, 1)
    cp = CairoPen(ctx)
    DATPen().rect(Rect(r)).replay(cp.flipped(r.h))
    ctx.fill()

    pat = cairo.LinearGradient(0.0, 0.0, r.w, r.h)
    # pat.add_color_stop_rgba(1, 0.7, 0, 1, 1)
    # pat.add_color_stop_rgba(0, 0.9, 0.7, 0.2, 1)
    pat.add_color_stop_rgba(1, 1, 1, 1, 1)
    pat.add_color_stop_rgba(0, 0, 0, 0, 1)
    ctx.set_source(pat)
    #ctx.set_source_rgb(0,0,0)
    # ctx.set_source_rgb(0.3, 0.2, random())  # Solid color

    cp = CairoPen(ctx)
    dt.replay(cp.flipped(r.h))

    ctx.fill()
    # ctx.set_line_width(4)
    # ctx.stroke()

    p = f"{dirname}/artifacts/example.png"
    surface.write_to_png(p)

    with previewer() as pv:
        pv.send(f"<img style='background:white' src='file:///{p}?q={random()}' width=150/>")

ss_test()
