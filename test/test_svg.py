import math
from test_preamble import *
from coldtype import StyledString, Slug, Style, Lockup
from coldtype.pens.svgpen import SVGPen
from coldtype.pens.outlinepen import OutlinePen
from coldtype.utils import transformpen
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.viewer import previewer
from coldtype.geometry import Rect, Point
from random import randint
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.misc.transform import Transform

def multilang_test(preview):
    r = Rect(0, 0, 700, 300)
    
    s1 = Slug("Hello, ", Style("¬/OhnoBlazeface12point.otf", 100, fill="deeppink", tracking=-10), margin=[0, -100])
    s2 = Slug(str(randint(2, 9)) + " worlds", Style("¬/OhnoBlazeface24point.otf", 100, baselineShift=100, fill="seagreen"))
    s3 = Slug(".", Style("¬/OhnoBlazeface72point.otf", 100, baselineShift=80, fill="black"), margin=[0, 0])

    lck = Lockup([s1,s2,s3])
    ps = lck.asPenSet()
    ps.align(r)
    preview.send(SVGPen.Composite(ps.pens + ps.frameSet().pens, r), r)

def no_glyph_sub_test(preview):
    r = Rect((0, 0, 500, 500))
    t = str(randint(0, 9))
    f, v = "¬/TweakDisplay-VF.ttf", dict(DIST=0.5, scale=True)
    #f, v = "¬/Eckmannpsych-Variable.ttf", dict(opsz=500)
    lck = Lockup([
        Slug("e", Style(f, 200, variations=v, features=dict(ss01=True))),
        Slug("π", Style("¬/VulfMonoRegular.otf", 200)),
    ])
    ps = lck.asPenSet().align(r)
    preview.send(SVGPen.Composite(ps.pens + ps.frameSet().pens, r), r)

def outline_test(preview):
    r = Rect(0, 0, 500, 500)
    ss = Slug("Yoy!", Style(font="≈/VulfSans-Black.otf", fontSize=300, tracking=-70, xShift=[0,-10,0,30], fill=(1, 0, 0.5, 0.5)))
    dps = ss.asPenSet()
    #dps.align(r)
    #dps.fromZero(r)
    #dps.align(r)
    #up = DATPen(fill=("random", 0.5)).rect(u)
    dps.align(r)
    preview.send(SVGPen.Composite(dps.frameSet().pens + dps.pens + [DATPen.Grid(r)], r), r)

def glyph_test(preview):
    r = Rect(0, 0, 1000, 300)
    st = Style("≈/CoFo_Peshka_Variable_V0.1.ttf", 100,
            tracking=-20, variations=dict(wdth=1), fill=(1, 0.5, 0), stroke=(0), strokeWidth=4)
    s = Slug("Hello World", st)
    #s.strings[0].addPath(DATPen().quadratic(r.inset(50, 10).point("SW"), r.point("N"), r.point("E")))
    ps = s.asPenSet().removeOverlap()
    ps.align(r)
    preview.send(SVGPen.Composite(list(reversed(ps.pens)) + ps.frameSet().pens, r), r)

def map_test(preview):
    f, v = ["≈/Fit-Variable.ttf", dict(wdth=0.2, scale=True)]
    f, v = ["≈/MapRomanVariable-VF.ttf", dict(wdth=1, scale=True)]
    ss = Slug("CALIFIA",
        Style(font=f,
        variations=v,
        fontSize=40,
        tracking=20,
        #tracking=21,
        #trackingLimit=21,
        baselineShift=0,
        ))
    rect = Rect(0,0,500,500)
    r = rect.inset(50, 0).take(180, "centery")
    dp = DATPen(fill=None, stroke="random").quadratic(r.p("SW"), r.p("C").offset(-100, 200), r.p("NE"))
    #ss.strings[0].addPath(dp, fit=True)
    ps = ss.asPenSet()
    ps.distributeOnPath(dp)
    preview.send(SVGPen.Composite(ps.pens + ps.frameSet().pens + [dp], rect), rect)


def pathops_test(p):
    r = Rect((0, 0, 500, 500))
    svg = SVGContext(r.w, r.h)
    r1 = DATPen().rect(r.inset(100, 100))
    r1.xor(DATPen().rect(r.inset(100, 100).offset(50, 50)))
    svg.addPath(r1, fill="green")

    track = r.take(100, "minx").inset(0, 40).take(40, "centerx")
    l1 = DATPen()
    l1.rect(track.take(1, "centerx", forcePixel=True))
    l1.rect(track.take(1, "centery", forcePixel=True))
    l1.difference(DATPen().oval(track.take(40, "maxy")))
    svg.addPath(l1, fill="blue")

    p.send(svg.toSVG())

def pattern_test(p):
    r = Rect((0, 0, 500, 500))
    svg = SVGContext(r.w, r.h)
    pattern = DATPen().rect(r.inset(150, 150).offset(200, -200))
    pattern.pattern(r)
    svg.addPath(pattern)
    p.send(svg.toSVG())

def catmull_test(pv):
    from random import randint
    r = Rect((0, 0, 500, 500))
    svg = SVGContext(r.w, r.h)
    dp = DATPen()
    points = []
    last_pt = (0, 0)
    for x in range(0, 10):
        too_close = True
        while too_close:
            pt = (randint(0, 500), randint(0, 500))
            if abs(last_pt[0] - pt[0]) > 100 and abs(last_pt[1] - pt[1]) > 100:
                too_close = False
            last_pt = pt
        points.append(last_pt)
    dp.catmull(points)
    dp.endPath()
    #dp.flatten()
    #dp.outline(offset=3)
    svg.addPath(dp, strokeWidth="4", stroke="black", fill="transparent")
    #svg.addPath(dp)
    pv.send(svg.toSVG())

with previewer() as p:
    #multilang_test(p)
    #no_glyph_sub_test(p)
    outline_test(p)
    #glyph_test(p)
    #map_test(p)
    #pathops_test(p)
    #pattern_test(p)
    #catmull_test(p)