import exrex

from coldtype import *
from coldtype.tool import Tool
from coldtype.osutil import show_in_finder


tool = Tool(ººinputsºº, dict(
    font=[None, str, "Must provide font regex or path", "Font search string"],
    scale=[1.25, float, None, "Scale for window (chars will size up to fill)"],
    variations=["{}", str, None, "Variations, as eval-able python string"],
    subset=[None, str, None, "Subset the font to only characters represented by this regex; hitting 2 in viewer will run pyftsubset with these characters"],
    dst=["~/Desktop", str, None, "Folder where subsetted fonts should appear"]
    )
    , ui=ººuiºº
    , name="Character Set Display"
    , doc="• Click something to see information printed in the terminal\n• Hit 1 in viewer to reveal current font in finder")


scale = tool.state["scale"]
r = Rect(1080*scale, 1080*scale + (h:=120))


if subset := tool.state["subset"]:
    subset = list(exrex.generate(subset))

fonts = tool.state["fonts"]
fnt:Font = fonts[0]

@animation(r, bg=1, tl=Timeline(len(fonts)))
def chars_display(f):
    global fnt
    fnt = fonts[f.i]
    chars = fnt.chars()

    if subset:
       chars = [(x, None) for x in subset]
    
    sq = math.ceil(math.sqrt(len(chars)))

    header, grid = f.a.r.divide(h, "N")
    rs = grid.inset(10).grid(sq, sq)

    return P(
        P(header).f(0),
        StSt(fnt.family, Font.JBMono(), 40, wght=1).align(header.inset(30), "N").f(1),
        StSt(fnt.fmtpath, Font.JBMono(), 20, wght=0.25).align(header.inset(25), "S").f(0.75),
        P().gridlines(grid, sq, sq),
        P().enumerate(chars, lambda x:
            StSt(x.el[0], fnt, rs[0].h-10, variations=eval(tool.state["variations"]))
                .data(char=x.el[0], gn=x.el[1])
                .f(0)
                .align(rs[x.i]))).data(fontPath=fnt.path)


numpad = {
    1: lambda _: show_in_finder(fnt.path),
    2: lambda _: fnt.subset((Path(tool.state["dst"]) / (fnt.path.stem + "_subset" + fnt.path.suffix)).expanduser(), text="".join(subset))
}


def on_click(pos):
    for m in (chars_display.last_return
        .find(lambda x: x.data("char") and pos.inside(x.ambit()))):
        char = m.data("char")
        print(f"> {char} \\u{ord(char):04X} {m.data('gn')}")