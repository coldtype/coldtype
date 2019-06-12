from test_preamble import *
from coldtype import StyledString, StyledStringSetter
from coldtype.svg import SVGContext
from coldtype.pens import OutlinePen
from furniture.viewer import previewer
from furniture.geometry import Rect
from random import randint


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
    ss = StyledString("Hello World", font="¬/CoFo_Peshka_Variable_V0.1.ttf", fontSize=100, tracking=-20)
    svg.addGlyph(ss.asGlyph(removeOverlap=True), fill="deeppink", stroke="black", strokeWidth=4)
    preview.send(svg.toSVG())

with previewer() as p:
    graff_test(p)
    #multilang_test(p)
    #no_glyph_sub_test(p)
    #outline_test(p)
    #rendering_test(p)
    #glyph_test(p)