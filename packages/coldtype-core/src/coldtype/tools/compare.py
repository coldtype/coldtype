from itertools import batched

from coldtype import *
from coldtype.tool import *


tool = Tool(ººinputsºº, dict(
    font=[Font.MutatorSans(), str, None, "Font search string"],
    text=["A", str, None, "Text to animate"],
    limit=[100, int, None, "How many to show (max)"])
    , print_fonts=False
    , name="Compare")

text = tool.state["text"]

fontpages:list[list[Font]] = list(batched(tool.state["fonts"], tool.state["limit"]))

header = 60

@animation((1080, 1080+header), tl=Timeline(len(fontpages), 24), bg=1)
def view(f):
    fonts = fontpages[f.i]
    sq = math.ceil(math.sqrt(len(fonts)))
    grid = f.a.r.drop(header, "S").inset(20).grid(sq, sq)
    return (P().enumerate(fonts, lambda x: 
        (StSt(text, x.el, grid[x.i].w*0.75, variations=tool.state["fontVariations"])
        .align(grid[x.i])
        .scaleToRect(grid[x.i].inset(2), shrink_only=1)
        .f(0)
        .data(font=x.el.path)))
        .append(P(f.a.r.take(header, "S"))
            .f(0))
        .append(StSt(f"{f.i+1}/{len(fontpages)}", Font.JBMono(), 30, wght=1)
            .f(1)
            .align(f.a.r.take(header, "S"))))


def on_click(pos):
    for m in (view.last_return
        .find(lambda x: x.data("font") and pos.inside(x.ambit()))):
        font = m.data("font")
        show_in_finder(font)
        print(f"> {font}")