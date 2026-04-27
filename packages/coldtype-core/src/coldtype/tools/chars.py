"""
Display characters available in a font
"""

from coldtype import *
from coldtype.tool import parse_inputs
from coldtype.osutil import show_in_finder

print(ººuiºº)

args = parse_inputs(ººinputsºº, dict(
    font=[None, str, "Must provide font regex or path"],
    rect=[Rect(1080), int]), ui=ººuiºº)


print("👉 Click something to see information printed in the terminal\n")


@animation(Rect(args["rect"].w, args["rect"].h+(h:=100)), bg=1, tl=Timeline(len(args["fonts"])))
def chars_display(f):
    fnt = args["fonts"][f.i]
    chars = fnt.chars()
    sq = math.ceil(math.sqrt(len(chars)))

    header, grid = f.a.r.divide(h, "N")
    rs = grid.inset(10).grid(sq, sq)

    return P(
        P(header).f(0),
        StSt(fnt.names()[0], fnt, 50).align(header).f(1),
        P().gridlines(grid, sq, sq),
        P().enumerate(chars, lambda x:
            StSt(x.el[0], fnt, rs[0].h-10, variations=args["font_variations"])
                .data(char=x.el[0], gn=x.el[1])
                .f(0)
                .align(rs[x.i]))).data(fontPath=fnt.path)


def build(_):
    show_in_finder(chars_display.last_return.data("fontPath"))


def on_click(pos):
    for m in (chars_display.last_return
        .find(lambda x: x.data("char") and pos.inside(x.ambit()))):
        char = m.data("char")
        print(f"> {char} \\u{ord(char):04X} {m.data('gn')}")