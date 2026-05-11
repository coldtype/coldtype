"""
Display available designspace
"""

from coldtype import *
from coldtype.tool import parse_inputs, fmt_path
from coldtype.fx.diagram import arrowhead
from coldtype.osutil import show_in_finder


args = parse_inputs(ººinputsºº, dict(
    font=[None, str, "Must provide font regex or path"]
    )
    , ui=ººuiºº)

sq = 9

@animation(Rect(args["rect"].w, args["rect"].h+(h:=120)), bg=1, tl=Timeline(len(args["fonts"])))
def dsview_display(f):
    fnt:Font = args["fonts"][f.i]
    path = fmt_path(fnt.path)

    variations = fnt.variations()
    axes = list(variations.keys())
    variations = list(variations.items())

    if len(axes) == 2:
        header, grid = f.a.r.divide(h, "N")

        def draw_glyph(x, y):
            r = y.el.inset(4)
            return (P(
                P(r).fssw(-1, 0, 1),
                StSt("B", fnt, 60, variations={axes[0]:x.e, axes[1]:y.e})
                    .align(r)
                    .f(0)
                    .data(font=fnt, position=dict(x=x.e, y=y.e))))

        return (P(
            P(header).f(0),
            StSt(fnt.names()[0], Font.JBMono(), 50, wght=1).scaleToRect(header.inset(30)).align(header.inset(30), "N").f(1),
            StSt(path, Font.JBMono(), 20, wght=0.25).align(header.inset(25), "S").f(0.75),
            horizontal:=StSt(fnt.getName(variations[0][1].get("axisNameID")) + " : " + variations[0][0], Font.JBMono(), 30, wght=1)
                .align(grid.drop(165, "W").take(75, "S"), "W")
                .f(0),
            vertical:=StSt(fnt.getName(variations[1][1].get("axisNameID")) + " : " + variations[1][0], Font.JBMono(), 30, wght=1)
                .rotate(90)
                .unframe()
                .align(grid.drop(165, "S").take(75, "W"), "S")
                .f(0),
            #StSt(axes[1], Font.JBMono(), 20, wght=0.5).rotate(90).align(grid.take(60, "W")),
            P().enumerate(grid.drop(60, "W").drop(60, "S").inset(10).subdivide(sq, "W"),
                lambda x: P().enumerate(x.el.subdivide(sq, "S"),
                    lambda y: draw_glyph(x, y))),
            
            P().line([p:=horizontal.ambit().pe.project(0, 30), p2:=p.project(0, ln:=350)]).ep()
                .line([p2, p2.project(45*3, ad:=20)]).ep()
                .line([p2, p2.project(-45*3, ad)]).ep()
                .fssw(-1, 0, 2),

            P().line([p:=vertical.ambit().pn.project(90, 30), p2:=p.project(90, ln)]).ep()
                .line([p2, p2.project(45*-1, ad)]).ep()
                .line([p2, p2.project(45*5, ad)]).ep()
                .fssw(-1, 0, 2),
        ).data(fontPath=fnt.path))

    return None


#def build(_):
#    show_in_finder(chars_display.last_return.data("fontPath"))


def on_click(pos):
    for m in (dsview_display.last_return
        .find(lambda x: x.data("position") and pos.inside(x.ambit()))):
        variations = list([v[1] for v in m.data("font").variations().items()])
        range_0 = variations[0].get("maxValue") - (min:=variations[0].get("minValue"))
        pos_0 = int(m.data("position").get("x")*range_0 + min)
        range_1 = variations[1].get("maxValue") - (min:=variations[1].get("minValue"))
        #print()
        #char = m.data("char")
        #print(f"> {char} \\u{ord(char):04X} {m.data('gn')}")