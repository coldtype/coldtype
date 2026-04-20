"""
Display characters available in a font; when glyph is clicked in viewer, print glyph/character information
"""

from coldtype import *
from coldtype.tool import parse_inputs

args = parse_inputs(__inputs__, dict(
    font=[None, str, "Must provide font regex or path"],
    fontSize=[72, int]))

fnt = args["font"]
chars = fnt.chars()

sq = math.ceil(math.sqrt(len(chars)))
fs = args["fontSize"]

def getGlyph(x):
    return StSt(x.el[0], fnt, fs, variations=args["font_variations"]).pen()

glyphs = P().enumerate(chars, getGlyph)

maxr:Rect = max([g.ambit(tx=1, ty=1) for g in glyphs])
maxr = maxr.square(outside=True).round().inset(-5).zero()

sq = math.ceil(math.sqrt(len(chars)))
rect = Rect(sq*maxr.w, sq*maxr.w)

print("👉 Click a symbol to see information printed in the terminal\n")

@ui(rect, bg=1)
def wt1(u):
    rs = u.r.inset(10).grid(sq, sq)
    
    def showChar(x):
        if u.c.inside(rs[x.i]): print(f"> {x.el[0]} \\u{ord(x.el[0]):04X} {x.el[1]}")
        return (P(glyphs[x.i].copy().f(0).align(rs[x.i])))

    return P(
        P().gridlines(u.r.inset(10), sq, sq),
        P().enumerate(chars, showChar))


def build(_):
    from coldtype.osutil import show_in_finder
    show_in_finder(fnt.path)