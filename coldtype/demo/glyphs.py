from coldtype import *
from coldtype.tool import parse_inputs

# TODO single-frame animated version?

args = parse_inputs(__inputs__, dict(
    font=[None, str, "Must provide font regex or path"],
    fontSize=[54, int],
    showChars=[False, bool]))

fnt = Font.Find(args["font"])

all_chars = []
cmap = fnt.font.ttFont["cmap"]
for ch, name in cmap.getBestCmap().items():
    all_chars.append(chr(ch))

sq = math.ceil(math.sqrt(len(all_chars)))

@ui(args["rect"])
def wt1(u):
    rs = u.r.inset(10).grid(sq, sq)
    
    def showChar(x):
        if u.c.inside(rs[x.i]):
            print(">", x.el)

        return PS([StSt(x.el, fnt, args["fontSize"])
                .align(rs[x.i])
                .f(0),
            P().text(x.el,
                Style("Times", 24
                    , load_font=0
                    , fill=hsl(0.8))
                , rs[x.i].inset(5)) if args["showChars"] else None])

    return P(
        P().gridlines(u.r.inset(10), sq, sq),
        P().enumerate(all_chars, showChar))