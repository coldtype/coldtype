from test_preamble import *
from coldtype import StyledString, StyledStringSetter
from coldtype.svg import SVGContext
from coldtype.pens import OutlinePen
from coldtype.beziers import simple_quadratic
from coldtype.utils import transformpen
from coldtype.datpen import DATPen
from furniture.viewer import previewer
from furniture.geometry import Rect
from random import randint
from fontTools.pens.recordingPen import RecordingPen, replayRecording


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
    ss = StyledString("New York City",
        font=f,
        variations=v,
        fontSize=40,
        tracking=-2,
        #tracking=21,
        #trackingLimit=21,
        baselineShift=-19,
        )
    r = svg.rect.inset(50, 0).take(180, "centery")
    rp = simple_quadratic(r.p("SW"), r.p("C").offset(-100, 200), r.p("NE"))
    ss.addPath(rp, fit=True)
    svg.addPath(rp, stroke="#eee", strokeWidth=1, fill="none")
    svg.addGlyph(ss.asGlyph(removeOverlap=True, atomized=False), fill="black")
    preview.send(svg.toSVG())

def vulf_logo(r, pen):
    a, bc = r.inset(30, 20).divide(80, "maxy")
    b, c = bc.take(90, "maxy").offset(0, -2).subdivide(2, "maxy")
    caps = dict(font="¬/VulfMonoLight.otf", fontSize=50, tracking=20, trackingLimit=-4)

    StyledString("vulf", font="¬/VulfMonoBlackItalic.otf", fontSize=68, tracking=0, rect=a, xShift=[0, 5, 6, 0]).asDAT().replay(pen)
    StyledString("COMPR", rect=b.inset(0, 0), **caps).asDAT().replay(pen)
    StyledString("ESSOR", rect=c.inset(0, 0), **caps).asDAT().replay(pen)

def faraday_logo(r, pen):
    a, b, c = r.inset(24, 20).take(0.9, "maxy").subdivide(3, "maxy")
    serif = "¬/WilliamTextPro-Italic.otf"
    sans = "¬/antiquegothic-regular.otf"
    #sans = "¬/Rainer_v0.2-Medium.otf"
    StyledString("Fara", font=serif, fontSize=72, tracking=20, rect=a).asDAT().replay(pen)
    StyledString("day", font=serif, fontSize=72, tracking=30, baselineShift=12, rect=b).asDAT().replay(pen)
    StyledString("LIMITER", font=sans, fontSize=100, tracking=5, baselineShift=-4, rect=c).asDAT().replay(pen)

def noun_ctrl(r, pen):
    a, b = r.inset(34, 20).take(0.9, "maxy").subdivide(2, "maxy")
    ctrl = StyledString("CTRL", font="¬/CovikSansMono-SemiBold.otf", fontSize=76, rect=b, baselineShift=10).asDAT()
    pen.record(ctrl)
    return a

def tone_ctrl(r, pen):
    a = noun_ctrl(r, pen)
    StyledString("TONE", font="¬/ObviouslyVariable.ttf", variations=dict(wdth=1, wght=0.6, slnt=0.5, scale=True), rect=a, fontSize=74, tracking=0).asDAT().replay(pen)

def trem_ctrl(r, pen):
    a = noun_ctrl(r, pen)
    StyledString("Trem", font="¬/Bahati0.1-Regular.otf", rect=a, fontSize=110, tracking=0, baselineShift=8).asDAT().replay(pen)

def wow_ctrl(r, pen):
    a = noun_ctrl(r, pen)
    StyledString("WOW", font="¬/HobeauxBold.otf", fontSize=76, rect=a).asDAT().replay(pen)

def lossy(r, pen):
    a, b = r.inset(30, 20).take(0.9, "maxy").subdivide(2, "maxy")
    f = "¬/italic 08_55.ttf"
    attrs = dict(font=f, fontSize=72, tracking=-5, align="CW")
    pen.record(StyledString("LOS", rect=a, **attrs).asDAT())
    pen.record(StyledString("SY", rect=b, **attrs).asDAT())

def midside(r, pen):
    a, b = r.inset(30, 30).take(0.9, "maxy").subdivide(2, "maxy")
    attrs = dict(fontSize=92, tracking=10)
    pen.record(StyledString("Mid", font="¬/GTHaptikLight.otf", rect=a, **attrs).asDAT())
    pen.record(StyledString("side", font="¬/GTHaptikLightRotalic.otf", rect=b, **attrs).asDAT())

def midside_matrix(r, pen):
    a, b, c = r.inset(30, 30).subdivide(3, "maxy")
    pen.record(StyledString("MID", font="¬/GTHaptikLight.otf", rect=a, fontSize=72, tracking=20).asDAT())
    pen.record(StyledString("SIDE", font="¬/GTHaptikLightRotalic.otf", rect=b, fontSize=72, tracking=12, baselineShift=-6).asDAT())
    pen.record(StyledString("MATRIX", font="¬/GTHaptikLight.otf", rect=c, fontSize=48, baselineShift=0).asDAT())

def megaverb(r, pen):
    a, b = r.inset(30, 30).take(0.9, "maxy").subdivide(2, "maxy")
    pen.record(StyledString("MEGA", font="¬/SenatorOT-Ultra.otf", fontSize=98, rect=a, align="CW").asDAT())
    pen.record(StyledString("verb", font="¬/RageItalicStd.otf", fontSize=138, baselineShift=30, rect=b, align="CE").asDAT())

def panpot(r, pen):
    a, b = r.inset(30, 30).take(0.8, "maxy").subdivide(2, "maxy")
    f = "¬/Eckmannpsych-Variable.ttf"
    attrs = dict(font=f, fontSize=102, tracking=0, variations=dict(opsz=0, scale=True))
    pen.record(StyledString("PAN", rect=a, **attrs).asDAT())
    pen.record(StyledString("POT", rect=b, **attrs).asDAT())

def lohi(r, pen):
    a = r.inset(30, 30).take(0.7, "maxy")
    f = "¬/GigV0.2-Regular.otf"
    pen.record(StyledString("LOHI", font=f, fontSize=92, baselineShift=[0, 0, 10, 10], rect=a).asDAT())

def logo_test(p, fn):
    r = Rect((0, 0, 248, 248))
    rp = DATPen()
    #vulf_logo(r, rp)
    fn(r, rp)
    svg = SVGContext(r.w, r.h)
    svg.addPath(rp, fill="black")
    p.send(svg.toSVG())

def number_test(p):
    svg = SVGContext(300, 300)
    ss = StyledString("51.78", font="¬/ObviouslyVariable.ttf", fontSize=300, features=dict(lnum=True, ss01=True), variations=dict(slnt=0.25, wght=1, scale=True))
    svg.addPath(ss.asRecording())
    p.send(svg.toSVG())

with previewer() as p:
    #graff_test(p)
    #multilang_test(p)
    #no_glyph_sub_test(p)
    #outline_test(p)
    #rendering_test(p)
    #glyph_test(p)
    #map_test(p)
    logo_test(p, vulf_logo)
    logo_test(p, faraday_logo)
    logo_test(p, wow_ctrl)
    logo_test(p, tone_ctrl)
    logo_test(p, trem_ctrl)
    logo_test(p, lossy)
    logo_test(p, megaverb)
    logo_test(p, midside)
    logo_test(p, midside_matrix)
    logo_test(p, panpot)
    logo_test(p, lohi)
    #number_test(p)