from coldtype import *
from coldtype.tool import parse_inputs

args = parse_inputs(__inputs__, dict(
    font=[None, str,
        "Must provide font regex or path"],
    fontSize=[72, int],
    showChars=[False, bool]))

fnt = Font.Find(args["font"])

all_chars = []
cmap = fnt.font.ttFont["cmap"]
for ch, name in cmap.getBestCmap().items():
    all_chars.append(chr(ch))

sq = math.ceil(math.sqrt(len(all_chars)))

@renderable((1000, 1000))
def wt1(r:Rect):
    rs = r.grid(sq, sq)
    return PS([
        P().gridlines(r, sq, sq),
        (PS.Enumerate(all_chars, lambda x:
            PS([
                StSt(x.el, fnt, args["fontSize"])
                    .align(rs[x.i])
                    .f(0),
                DATText(x.el, Style("Times", 24, load_font=0, fill=hsl(0.8)), rs[x.i].inset(5)) if args["showChars"] else None])))])