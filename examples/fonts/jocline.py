from coldtype import *
from coldtype.renderable.font import generativefont, glyphfn

from textwrap import indent

r0 = Rect(750, 750)
rs = r0.grid(2, 2)

outline = 11

cs, cm, cl = P().oval(r0.inset(250)), P().oval(r0.inset(125)), P().oval(r0)
curves = (P(
    cl.copy().intersection(P(rs[0])).difference(cs).difference(cm),
    cm.copy().intersection(P(rs[0])).difference(cs),
    cs.copy().intersection(P(rs[0])))
    .outline(outline)
    .data(frame=rs[0]))

straights = (P(rs[0].subdivide(3, "W"))
    .outline(outline)
    .data(frame=rs[0]))

def quad(idx, curved, rotation=0, reverse=0):
    p = curves.copy() if curved else straights.copy()
    p.align(rs[idx])
    
    if curved:
        if idx == 1:
            p.rotate(-90)
        elif idx == 2:
            p.rotate(90)
        elif idx == 3:
            p.rotate(180)

    p.rotate(rotation*90)
    #p.difference(p.copy().outline(10).reverse())
    #p.outline(2)
    if reverse:
        p.reverse()
    return p

spacing = 8

def quads(*pairs):
    qs = []
    for idx, pair in enumerate(pairs):
        if pair is None:
            continue
        if isinstance(pair, int):
            qs.append(quad(idx, pair))
        else:
            qs.append(quad(idx, *pair))
    return P(qs)

spr = 20
sps = 40

@glyphfn(200)
def space(): return P()

@glyphfn("auto", spr, sps, cover_lower=1)
def A(): return quads(1, 1, [1, 3], [0, 2])

@glyphfn("auto", sps, spr, cover_lower=1)
def B(): return quads(0, 1, 1, 1)

@glyphfn("auto", spr, sps)
def c(): return quads(1, None, 1, None)

@glyphfn("auto", spr, sps)
def C(): return quads(1, [0, 3], 1, [0, 1])

@glyphfn("auto", spr, sps)
def d(): return quads(1, [0, 2], 1, 1)

@glyphfn("auto", sps, spr)
def D(): return quads([0, 1], 1, [0, 1], 1)

@glyphfn("auto", spr, sps, cover_lower=1)
def E(): return quads(1, 1, 1, [0, 1])

@glyphfn("auto")
def f(): return quads(1, 1, [0, 0], [0, 3])

@glyphfn("auto")
def F(): return quads([1, 0], [0, 3], [0, 0], [0, 3])

@glyphfn("auto", spr, cover_lower=1)
def G(): return quads(1, [0, 1], 1, 0)

#def H(): return quads(0, [0, 0, 1], 0, [0, 0, 1])
@glyphfn("auto", cover_lower=1)
def H(): return quads(0, 1, 0, [0, 2])

@glyphfn("auto", cover_lower=1)
def I(): return quads([0, 2], None, [0, 2], None)

@glyphfn("auto", cover_lower=1)
def J(): return quads(None, [0, 2], None, 1)

@glyphfn("auto", sps, spr, cover_lower=1)
def K(): return quads(0, [1, 3], 0, [1, 1])

@glyphfn("auto", cover_lower=1)
def L(): return quads(0, None, 1, None)

@glyphfn("auto", cover_lower=1)
def M(): return quads([1, 3], 1, [0, 2], [0, 2])

@glyphfn("auto", cover_lower=1)
def N(): return quads(1, 1, 0, [0, 2])

@glyphfn("auto")
def N_ss01(): return quads(0, 1, 0, [0, 2])

@glyphfn("auto", spr, spr, cover_lower=1)
def O(): return quads(1, 1, 1, 1)

@glyphfn("auto", sps, spr, glyph_name="P", cover_lower=1)
def _P(): return quads(1, 1, 0, 1)

@glyphfn("auto", spr, sps, cover_lower=1)
def Q(): return quads(1, 1, 1, 0)

@glyphfn("auto")
def r(): return quads(1, None, 0, None)

@glyphfn("auto")
def R(): return quads(1, 1, 0, [1, 3])

@glyphfn("auto")
def R_ss01(): return quads(1, 1, 0, [1, 1])

@glyphfn("auto")
def s(): return quads([1, 0], None, [1, 1], None)

@glyphfn("auto")
def S(): return quads(1, [0, 3], [0, 1], 1)

@glyphfn("auto", cover_lower=1)
def T(): return quads(0, 0, 1, 0)

@glyphfn("auto")
def T_ss01(): return quads([0, 1], [0, 1], [1, 0], [0, 1])

@glyphfn("auto", cover_lower=1)
def U(): return quads(0, [0, 2], 1, [0, 2])

@glyphfn("auto", cover_lower=1)
def V(): return quads(0, [0, 2], 1, 1)

@glyphfn("auto", cover_lower=1)
def W(): return quads(0, 0, 1, [1, 3])

@glyphfn("auto", cover_lower=1)
def X(): return quads([1, 1], [1, 3], [1, 3], [1, 1])

@glyphfn("auto", cover_lower=1)
def Y(): return quads([1, 1], [0, 2], 1, 1)

@glyphfn("auto", cover_lower=1)
def Z(): return quads([0, 3, 1], [1, 0, 1], [1, 0, 1], [0, 1, 1])

@glyphfn("auto")
def one(): return quads(None, 1, None, 0)

@glyphfn("auto")
def two(): return quads(1, 1, [1, 3], [0, 1])

@glyphfn("auto")
def three(): return quads([0, 1], [1, 3], [0, 1], [1, 1])

@glyphfn("auto")
def four(): return quads(1, 0, [0, 1], 0)

@glyphfn("auto")
def five(): return quads([0, 1], [0, 1], [0, 1], 1)

@glyphfn("auto")
def six(): return quads(1, [0, 1], 1, 1)

@glyphfn("auto")
def seven(): return quads([0, 1], [0, 1], [1, 3], 1)

@glyphfn("auto")
def eight(): return quads(1, 1, [1, 3], [1, 5])

@glyphfn("auto")
def nine(): return quads(1, 1, [0, 1], 1)

@glyphfn("auto")
def zero(): return quads(1, 1, 1, 1)

@glyphfn("auto")
def question(): return quads(1, 1, [1, 3, 1], 1)

def show_grid(p):
    grid = (P().enumerate(rs, lambda x: P(
        StSt(str(x.i), Font.JBMono(), 100).align(x.el).f(hsl(0.7, a=0.3)),
        P(x.el).fssw(-1, hsl(0.9), 1))))
    return grid.tag("guide") + p

@generativefont(globals(),
    ººsiblingºº("jocline.ufo"),
    "Joc Line",
    "Regular",
    preview_size=(1300, None),
    default_lsb=sps,
    default_rsb=sps,
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
        return StSt("BANJO", Font(gufo.fontmake_path(find=True)), 160, ss01=0).align(r, ty=1).f(0)
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