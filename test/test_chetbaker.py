from coldtype import *
from coldtype.warping import warp_fn

import cv2
import numpy as np

r = Rect(1080, 1080)

from fontTools.misc.bezierTools import splitCubicAtT

obv = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")
tl = Timeline(60)

lockup = (Composer(r,
    "MILES DAVIS\nJAZZ DOCUMENTARY",
    #"LO! THERE",
    Style(obv, 250, wdth=0.25, wght=0.15, slnt=0, ss01=1),
    leading=50,
    fit=r.w-250)
    .pens()
    .xa()
    .align(r)
    )

@animation(r, timeline=tl, bg=0)
def stub(f):
    ri = r
    bc = (DATPen()
        .moveTo(ri.psw)
        .boxCurveTo(ri.pse.offset(0, 200), "NW", 0.35))
    bc2 = (DATPen()
        .moveTo(ri.pnw)
        .boxCurveTo(ri.pne.offset(0, -200),
        "SW", 0.35))

    e = f.a.progress(f.i, loops=1, easefn="eeio").e
    src = np.array((
        r.pnw,
        r.pne,
        r.psw,
        r.pse,
        #r.pc
        ),
        dtype=np.float32)
    dest = np.array(((
        r.pnw.offset(0, 0),
        r.pne.offset(0, 0),
        r.psw.offset(690*e, 0),
        r.pse.offset(-690*e, 0),
        #r.pc
        )),
        dtype=np.float32)
    #mtx = cv2.findHomography(src, dest)
    #print(mtx)
    mtx = cv2.getPerspectiveTransform(src, dest)
    #print(mtx)

    out = DATPens()
    to_warp = lockup.copy().collapse()
    to_warp = DATPen().gridlines(f.a.r).explode()
    for p in to_warp:
        fvl = np.array((p.flatten(25).fvl(),), dtype=np.float32)
        converted = cv2.perspectiveTransform(fvl, mtx)
        #converted = cv2.warpPerspective(fvl, mtx, fvl.shape[:-1])
        out += DATPen().line(converted[0])
    return out.f(0).s(1).sw(3)

    return DATPens([
        DATPens([
            bc,
            bc2
        ]).f(None).s(hsl(0.9)).sw(15),
        (l
        -.phototype(f.a.r, blur=5, cut=100+(1-f.a.progress(f.i, loops=1, easefn="qeio").e)*150, cutw=8.5))
    ])