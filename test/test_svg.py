import math
from test_preamble import *
from coldtype import StyledString, StyledStringSetter
from coldtype.svg import SVGContext
from coldtype.pens import OutlinePen
from coldtype.beziers import simple_quadratic
from coldtype.utils import transformpen
from coldtype.datpen import DATPen
from furniture.viewer import previewer
from furniture.geometry import Rect, Point
from random import randint
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.misc.transform import Transform


def graff_test(preview):
    txt = "ABC{:02d}".format(randint(0, 100))
    #txt = "Graphics"
    #txt = "2019"
    #txt = "NYC"
    svg = SVGContext(1000, 1000)
    f, v = ["¬/Beastly-12Point.otf", dict()]
    f, v = ["¬/ObviouslyVariable.ttf", dict(wdth=.5, wght=1, slnt=1, scale=True)]
    #f, v = ["¬/Cheee_Variable.ttf", dict(grvt=0.3, yest=1, scale=True)]
    f, v = ["¬/Fit-Variable.ttf", dict(wdth=1, scale=True)]
    f, v = ["¬/CoFo_Peshka_Variable_V0.1.ttf", dict(wdth=1, wght=1, scale=True)]
    ss = StyledString(txt, font=f, fontSize=500, variations=v, tracking=-30)
    ss.place(svg.rect.inset(140, 0))
    svg.addOval(svg.rect.take(ss.ch*ss.scale(), "centery"), fill="deeppink", stroke="seagreen", strokeWidth=20)
    for g in reversed(ss.asGlyph(removeOverlap=True, atomized=True)):
        svg.addGlyph(g, fill="royalblue", stroke="black", strokeWidth=10)
    preview.send(svg.toSVG())

def multilang_test(preview):
    svg = SVGContext(1000, 1000)
    sss = StyledStringSetter([
        StyledString("Hello, ", font="¬/OhnoBlazeface12point.otf", fontSize=100, rightMargin=-100, fill="deeppink"),
        StyledString(str(randint(2, 9)) + " worlds", font="¬/OhnoBlazeface24point.otf", fontSize=100, baselineShift=100, fill="seagreen"),
        StyledString(".", font="¬/OhnoBlazeface72point.otf", fontSize=100, leftMargin=-40, baselineShift=0, fill="black"),
        ])
    
    sss.align(rect=svg.rect)
    for s in sss.strings:
        svg.addPath(s.asRecording(), fill=s.fill)
    preview.send(svg.toSVG())

def no_glyph_sub_test(preview):
    r = Rect((0, 0, 1000, 1000))
    t = str(randint(0, 9))
    f, v = "¬/TweakDisplay-VF.ttf", dict(DIST=0.5, scale=True)
    #f, v = "¬/Eckmannpsych-Variable.ttf", dict(opsz=500)
    sss = StyledStringSetter([
        StyledString("e", font=f, fontSize=500, variations=v, features=dict(ss01=True)),
        StyledString("π", "¬/VulfMonoRegular.otf", fontSize=500),
    ])
    sss.align(rect=r)
    preview.send(wrap_svg_paths(pen_to_svg(sss.asRecording(), r), r))

def outline_test(preview):
    svg = SVGContext(1000, 1000)
    t = "ABC"
    f, v = ["¬/Cheee_Variable.ttf", dict(grvt=0.8, yest=1, temp=0, scale=True)]
    ss = StyledString(t, font=f, fontSize=300, variations=v, tracking=-40)
    ss.place(svg.rect)
    rp = ss.asRecording()
    svg.addPath(rp, fill="hotpink")
    svg.addPath(OutlinePen.Record(ss.asRecording(), offset=4))
    preview.send(svg.toSVG())

def rendering_test(preview):
    svg = SVGContext(1000, 200)
    f = "¬/GTHaptikLight.otf"
    f = "¬/Gooper0.2-BlackItalic.otf"
    f = "¬/SourceSerifPro-BlackIt.ttf"
    ss = StyledString("MONO BELOW".upper(), font=f, fontSize=32, tracking=3, rect=svg.rect)
    svg.addPath(ss.asRecording(rounding=3), fill="black")
    preview.send(svg.toSVG())
    import drawBot as db
    db.newDrawing()
    db.size(svg.rect.w, svg.rect.h)
    fs = ss.formattedString()
    bp = db.BezierPath()
    bp.text(fs, ss._final_offset)
    db.drawPath(bp)
    #db.text(fs, (100, 100))
    db.saveImage(dirname + "/scratch.svg")
    with open(dirname + "/scratch.svg", "r") as f:
        preview.send(f.read())
    db.endDrawing()

def glyph_test(preview):
    svg = SVGContext(1000, 300)
    ss = StyledString("Hello World", font="¬/CoFo_Peshka_Variable_V0.1.ttf", fontSize=100, tracking=-20, rect=svg.rect)
    svg.addGlyphs(reversed(ss.asGlyph(removeOverlap=True, atomized=True)), fill="deeppink", stroke="black", strokeWidth=4)
    preview.send(svg.toSVG())

def map_test(preview):
    f, v = ["¬/Fit-Variable.ttf", dict(wdth=0.2, scale=True)]
    f, v = ["¬/MapRomanVariable-VF.ttf", dict(wdth=1, scale=True)]
    svg = SVGContext(500, 500)
    ss = StyledString("CALIFIA",
        font=f,
        variations=v,
        fontSize=40,
        tracking=20,
        #tracking=21,
        #trackingLimit=21,
        baselineShift=0,
        )
    r = svg.rect.inset(50, 0).take(180, "centery")
    rp = simple_quadratic(r.p("SW"), r.p("C").offset(-100, 200), r.p("NE"))
    ss.addPath(rp, fit=True)
    svg.addPath(rp, stroke="#eee", strokeWidth=1, fill="none")
    svg.addGlyph(ss.asGlyph(removeOverlap=True, atomized=False), fill="black")
    preview.send(svg.toSVG())

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
    #graff_test(p)
    #multilang_test(p)
    #no_glyph_sub_test(p)
    #outline_test(p)
    #rendering_test(p)
    #glyph_test(p)
    #map_test(p)
    #pathops_test(p)
    #pattern_test(p)
    catmull_test(p)