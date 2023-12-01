from coldtype import *
from coldtype.renderable.font import generativefont, glyphfn
from textwrap import indent

VERSIONS = {
    "Regular": dict(),
    "Front": dict(),
    "Back": dict(),
    "Lines": dict(),
    "FilledFront": dict(),
} #/VERSIONS

spr = 0
sps = 10

basis = Font.Find("HEX Franklin v0.2 v")

version = __VERSION__["key"]
print(">>>>>>>>>>", version)

def offset(c, *points, adds=[]):
    _offset = (233, 217)
    #_offset = (420, 480)

    glyph = (StSt(c, basis, 1000, wght=1, wdth=0.4)
        .pen()
        .ro()
        .q2c()
        .data(frame=None))

    for idx, t, in adds:
        glyph.add_pt_t(idx, t)

    doubled = (glyph.copy()
        .outline(6, miterLimit=4)
        .ro()
        .layer(1, lambda p: p.t(*_offset))
        .insert(0, glyph.copy().tag("guide")))
    
    if points and points[0] == "auto":
        line_pts = []
        for idx, (mv, _) in enumerate(glyph._val.value):
            if mv in ["moveTo", "lineTo"]:
                if idx not in points:
                    line_pts.append(idx)
        points = line_pts

    def liner(x):
        pt = Point(*glyph._val.value[x.el][1][-1])
        return (P()
            .line([pt, pt.o(*_offset)])
            .outline(6, cap="butt")
            .reverse())
    
    lines = P().enumerate(points, liner)
    doubled.append(lines)

    frame = doubled.bounds()
    
    if version in ["Regular", "Lines"]:
        lines = P().enumerate(points, liner)
        if version == "Lines":
            return lines.data(frame=frame)
        elif version == "Regular":
            return doubled
    else:
        if version == "Front":
            return doubled[1].data(frame=frame)
        elif version == "Back":
            return doubled[2].data(frame=frame)
        elif version == "FilledFront":
            return (glyph.copy()
                .difference(glyph.copy().outline(12, miterLimit=4).ro())
                .data(frame=frame)
                )
        return doubled

@glyphfn(200)
def space(): return P()

@glyphfn("auto", spr, spr, cover_lower=1)
def A(): return offset("A", "auto")

@glyphfn("auto", sps, spr, cover_lower=1)
def B():
    return offset("B", 10, 28, 27, 12, 18, 0, 5, 2)
    
@glyphfn("auto", spr, spr, cover_lower=1)
def C():
    return offset("C", 15, 16, 3, 2, 20, 5, 12, 1)

@glyphfn("auto", sps, spr, cover_lower=1)
def D():
    return offset("D", 8, 21, 20, 18, 0, 2)

@glyphfn("auto", sps, sps, cover_lower=1)
def E(): return offset("E", "auto")

@glyphfn("auto", sps, sps, cover_lower=1)
def F(): return offset("F", "auto")

@glyphfn("auto", spr, spr, cover_lower=1)
def G():
    return offset("G",
        25, 17, 20, 21, 5, 6, 7, 8, 4, 3)

@glyphfn("auto", sps, sps, cover_lower=1)
def H(): return offset("H", "auto")

@glyphfn("auto", sps, sps, cover_lower=1)
def I(): return offset("I", "auto")

@glyphfn("auto", spr, sps, cover_lower=1)
def J(): return offset("J", 0, 10, 8, 6, 5, 3)

@glyphfn("auto", sps, spr, cover_lower=1)
def K(): return offset("K",
    0, 1, 4, 5, 13, 12, 10, 9, 7, 11, 2, 3)

@glyphfn("auto", sps, sps, cover_lower=1)
def L(): return offset("L", "auto")

@glyphfn("auto", sps, sps, cover_lower=1)
def M(): return offset("M", "auto")

@glyphfn("auto", sps, sps, cover_lower=1)
def N(): return offset("N", "auto")

@glyphfn("auto", sps, spr, cover_lower=1)
def O(): return offset("O", 7, 21, 29, 1)

@glyphfn("auto", sps, spr, cover_lower=1, glyph_name="P")
def _P(): return offset("P", 0, 1, 8, 10, 16, 4, 14, 2)

@glyphfn("auto", spr, spr, cover_lower=1)
def Q(): return offset("Q", 11, 28, 36, 2, 1, 5)

@glyphfn("auto", sps, spr, cover_lower=1)
def R(): return offset("R", 12, 20, 21, 0, 1, 5, 6, 2, 7)

@glyphfn("auto", spr, spr, cover_lower=1)
def S(): return offset("S", 2, 20, 15, 16, 34, 33, 30, 12, adds=[[1, 0.5], [19, 0.5]])

@glyphfn("auto", spr, spr, cover_lower=1)
def T(): return offset("T", "auto")

@glyphfn("auto", sps, spr, cover_lower=1)
def U(): return offset("U", 6, 1, 11, 10, 4, 3)

@glyphfn("auto", spr, spr, cover_lower=1)
def V(): return offset("V", "auto")

@glyphfn("auto", spr, spr, cover_lower=1)
def W(): return offset("W", "auto")

@glyphfn("auto", spr, spr, cover_lower=1)
def X(): return offset("X", "auto")

@glyphfn("auto", spr, -20, cover_lower=1)
def Y(): return offset("Y", "auto")

@glyphfn("auto", spr, spr, cover_lower=1)
def Z(): return offset("Z", "auto")

@glyphfn("auto", spr, spr, cover_lower=1)
def nine(): return offset("9", 1, 31, 16, 15, 26, 19)

@glyphfn("auto", spr, spr, cover_lower=1)
def exclam(): return offset("!", "auto")

def show_grid(p):
    return p
    try:
        original = p.find("guide")[0]
        original.fssw(hsl(0.3, a=0.1), 0, 0)
        pts = P()
        for idx, pt in enumerate(original._val.value):
            if pt[1]:
                pts.append(StSt(str(idx), Font.JBMono(), 40).t(*pt[1][-1]))
        return pts.tag("guide") + p[1:]
    except Exception as e:
        print(e)
        return p

@generativefont(globals(),
    ººsiblingºº(f"bombere_{version.lower()}.ufo"),
    "Bombere",
    version,
    preview_size=(1300, 1100),
    default_lsb=sps,
    default_rsb=sps,
    ascender=1000,
    cap_height=1000,
    filter=show_grid,
    bg=1)
def gufo(f):
    return gufo.glyphViewer(f)

@animation((1080, 270), tl=gufo.timeline)
def spacecenter(f):
    #return gufo.spacecenter(f.a.r, "auto", idx=f.i)
    try:
        glyphs = P([gf.glyph_with_frame(gufo) for gf in gufo.glyph_fns])
        return (glyphs.spread(10)
            .scale(0.2, pt=(0,0))
            .f(0)
            .centerPoint(f.a.r, (f.i, "C")))
    except:
        return None

@renderable((1080, 290))
def smoke(r):
    try:
        return StSt("GOODHERTZ\n9 YEAR SALE\nANNIVERSARY!", Font(gufo.fontmake_path(find=True)), 72, ss01=0).align(r, ty=1).f(0)
    except FontNotFoundException:
        return None

def release(_):
    [gufo.buildGlyph(gf) for gf in gufo.glyph_fns]

    ss01 = []
    for gf in gufo.glyph_fns:
        if "_ss01" in gf.glyph_name:
            plain = gf.glyph_name.split("_")[0]
            ss01.append(f"sub {plain} by {gf.glyph_name};")
    
    ss01 = indent("\n".join(ss01), "    ")

    features = f"""languagesystem DFLT dflt;
languagesystem latn dflt;

feature ss01 {{
{ss01}
}} ss01;"""
    gufo.fontmake(version="a1", features=features)