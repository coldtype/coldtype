from test_preamble import *

import importlib
import coldtype
importlib.reload(coldtype)

from coldtype.geometry import Rect
from drawBot import *


def normalizeBezier(bp_or_g):
    bp = bp_or_g
    bp = BezierPath()
    try:
        bp_or_g.drawToPen(bp)
    except:
        bp_or_g.draw(bp)
    return bp


def drawBezier(bp_or_g):
    bp = normalizeBezier(bp_or_g)
    drawPath(bp)
    return bp


def drawBezierSkeleton(bp_or_g, r=4, points=True, handles=True, labels=True, randomize=False, f=True, s=True):
    bp = normalizeBezier(bp_or_g)
    with savedState():
        stroke(None)
        if f:
            if randomize:
                fill(random(), random(), random(), 0.5)
            else:
                fill(0, 0.2)
            drawPath(bp)
        fill(None)
        if s:
            if randomize:
                stroke(random(), random(), random(), 0.5)
            else:
                stroke(0, 0.5)
            drawPath(bp)
        stroke(None)
        font("InputMonoCompressed-Bold")
        fontSize(10)
        if randomize:
            fill(random(), random(), random(), 0.8)
        else:
            fill(0, 0.5)
        if points:
            for i, p in enumerate(bp.onCurvePoints):
                x, y = p
                if i == 0:
                    rect(x-r*2, y-r*2, r*4, r*4)
                else:
                    rect(x-r, y-r, r*2, r*2)
                if labels:
                    text("({:0.2f}, {:0.2f})".format(x, y), (x+10, y-10))
        if randomize:
            fill(random(), random(), random(), 0.8)
        else:
            fill(1, 0, 0.5, 0.5)
        if handles:
            for p in bp.offCurvePoints:
                x, y = p
                oval(x-r, y-r, r*2, r*2)
                if labels:
                    text("({:0.2f}, {:0.2f})".format(x, y), (x+10, y-10))
    return bp


def grid(r, color=None):
    with savedState():
        if color:
            fill(*color)
        for i, column in enumerate(r.pieces(40, "minx")):
            for j, box in enumerate(column.pieces(40, "maxy")):
                if (i % 2 == 0 and j % 2 == 1) or (i % 2 == 1 and j % 2 == 0):
                    rect(*box)