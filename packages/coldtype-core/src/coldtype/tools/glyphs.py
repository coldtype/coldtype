from coldtype import *
from coldtype.tool import parse_inputs

# TODO single-frame animated version?

args = parse_inputs(__inputs__, dict(
    font=[None, str, "Must provide font regex or path"],
    fontSize=[100, int]))

fnt = args["font"]
os2 = fnt.font.ttFont["OS/2"]
glyphSet = fnt.font.ttFont.getGlyphSet()
els = glyphSet.keys()
fs = args["fontSize"]

glyphs = P().enumerate(els, lambda x: P()
    .glyph(glyphSet[x.el], glyphSet)
    .f(0)
    .scale(fs/fnt.metrics.upem, pt=(0,0)))

maxr:Rect = max([g.ambit() for g in glyphs])
maxr = maxr.square(outside=True).round().inset(-10).zero()

sq = math.ceil(math.sqrt(len(els)))
rect = Rect(sq*maxr.w, sq*maxr.w)

@ui(rect, bg=1)
def wt1(u):
    rs = u.r.inset(10).grid(sq, sq)
    
    def showChar(x):
        if u.c.inside(rs[x.i]): print(">", x.el)
        return glyphs[x.i].copy().align(rs[x.i])

    return P(
        P().gridlines(u.r.inset(10), sq, sq),
        P().enumerate(els, showChar))


def build(_):
    from coldtype.osutil import show_in_finder
    show_in_finder(fnt.path)