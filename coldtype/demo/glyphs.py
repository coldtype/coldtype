from coldtype import *
from coldtype.tool import parse_inputs

# TODO single-frame animated version?

args = parse_inputs(__inputs__, dict(
    font=[None, str, "Must provide font regex or path"],
    fontSize=[54, int],
    showChars=[False, bool]))

fnt = Font.Find(args["font"])

by_char = False

if by_char:
    all_chars = []
    cmap = fnt.font.ttFont["cmap"]
    for ch, name in cmap.getBestCmap().items():
        all_chars.append(chr(ch))
    els = all_chars
else:
    os2 = fnt.font.ttFont["OS/2"]
    glyphSet = fnt.font.ttFont.getGlyphSet()
    els = glyphSet.keys()

sq = math.ceil(math.sqrt(len(els)))
fs = args["fontSize"]

@ui(args["rect"], bg=1)
def wt1(u):
    rs = u.r.inset(10).grid(sq, sq)
    
    def showChar(x):
        if u.c.inside(rs[x.i]):
            print(">", x.el)

        if by_char:
            return P(StSt(x.el, fnt, fs)
                    .align(rs[x.i])
                    .f(0),
                P().text(x.el,
                    Style("Times", 24
                        , load_font=0
                        , fill=hsl(0.8))
                    , rs[x.i].inset(5)) if args["showChars"] else None)
        else:
            glyph = glyphSet[x.el]
            return (P()
                .glyph(glyph, glyphSet).f(0).scale(fs/750, pt=(0, 0))
                .align(rs[x.i])
                .scaleToRect(rs[x.i].inset(6), shrink_only=1, preserveAspect=1))

    return P(
        P().gridlines(u.r.inset(10), sq, sq),
        P().enumerate(els, showChar))