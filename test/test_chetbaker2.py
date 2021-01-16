from coldtype import *
from coldtype.warping import warp_fn

from pygem import IDW
import cv2
import numpy as np


r = Rect(1080, 1080)

from fontTools.misc.bezierTools import splitCubicAtT

obv = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")
tl = Timeline(60)

lockup = (Composer(r,
    "MILES DAVIS\nJAZZ DOCUMENTARY",
    #"LO! THERE",
    Style(obv, 250, wdth=0.25, wght=0.75, slnt=0, ss01=1),
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

    rs = r.grid(2, 2)
    srcs = []
    dsts = []
    mtxs = []

    pc = r.pc
    pco = r.pc.offset(0, 250)

    for idx, rr in enumerate(rs):
        ps = rr.pnw, rr.pne, rr.psw, rr.pse
        src = np.array(
            ps,
            dtype=np.float32)
        dst = np.array(
            [pco if p == pc else p for p in ps],
            dtype=np.float32)
        mtxs.append(cv2.getPerspectiveTransform(src, dst))

    src = np.array((
        r.pnw,
        r.pne,
        r.psw,
        r.pse
        ),
        dtype=np.float32)
    dest = np.array(((
        r.pnw.offset(0, 0),
        r.pne.offset(0, 0),
        r.psw.offset(e*1000, 0),
        r.pse.offset(0, e*1000)
        )),
        dtype=np.float32)

    mtx = cv2.getPerspectiveTransform(src, dest)

    out = DATPens()
    to_warp = lockup.copy().collapse()
    #to_warp = [DATPen().gridlines(f.a.r).outline().pen()]
    for p in to_warp:
        def transform(x, y):
            pxy = Point([x, y])
            for idx, rr in enumerate(rs):
                if pxy.inside(rr):
                    mtx = mtxs[idx]
                    p = (x, y)
                    px = (mtx[0][0]*p[0] + mtx[0][1]*p[1] + mtx[0][2]) / ((mtx[2][0]*p[0] + mtx[2][1]*p[1] + mtx[2][2]))
                    py = (mtx[1][0]*p[0] + mtx[1][1]*p[1] + mtx[1][2]) / ((mtx[2][0]*p[0] + mtx[2][1]*p[1] + mtx[2][2]))
                    p_after = (int(px), int(py))
                    return p_after
        
        out += p.flatten(10).nlt(transform)

    return DATPens([
        DATPens([
            #bc,
            #bc2
        ]).f(None).s(hsl(0.9)).sw(15),
        (out.f(1)
        -.phototype(f.a.r, blur=5, cut=210, cutw=3.5))
    ])