"""
Display available designspace
"""

from coldtype import *
from coldtype.tool import parse_inputs, fmt_path
from coldtype.fx.diagram import arrowhead
from coldtype.osutil import show_in_finder


args = parse_inputs(ººinputsºº, dict(
    font=[Font.MutatorSans(), str],
    text=["A", str],
    count=[9, int],
    axes=["0,1", str],
    )
    , ui=ººuiºº)


A, B = [int(x) for x in args["axes"].split(",")]
a, b = A, B


@animation(Rect(args["rect"].w, args["rect"].h+(h:=120)), bg=1, tl=Timeline(len(args["fonts"])))
def dsview_display(f):
    global a, b

    fnt:Font = args["fonts"][f.i]
    path = fmt_path(fnt.path)

    variations = fnt.variations()
    axes = list(variations.keys())
    variations = list(variations.items())

    if len(axes) == 1:
        a, b = 0, 0
    else:
        a, b = A, B

    out = P()

    header, grid = f.a.r.divide(h, "N")

    def draw_glyph(x, y):
        r = y.el.inset(4)
        return (P(
            StSt(args["text"], fnt, args["fontSize"], variations={axes[a]:x.e, axes[b]:y.e})
                .align(r)
                .f(0)
                .data(font=fnt, position=dict(x=x.e, y=y.e))))

    out = (P(
        P(header).f(1),
        StSt(fnt.names()[0], Font.JBMono(), 40, wght=1).align(header.inset(25), "NE").f(0),
        StSt(path, Font.JBMono(), 22, wght=0.25).align(header.inset(25), "SE").f(0),
        
        horizontal:=StSt(fnt.getName(variations[a][1].get("axisNameID")) + f" : “{variations[a][0]}” ", Font.JBMono(), 24, wght=1)
            .align(grid.drop(165, "W").take(75, "S"), "W")
            .f(0),
        vertical:=StSt(fnt.getName(variations[b][1].get("axisNameID")) + f" : “{variations[b][0]}” ", Font.JBMono(), 24, wght=1)
            .rotate(90)
            .unframe()
            .align(grid.drop(165, "S").take(75, "W"), "S")
            .f(0),
            
        P().enumerate((g:=grid.drop(75, "W").drop(75, "S").inset(0)).subdivide(args["count"], "W"),
            lambda x: P().enumerate(x.el.subdivide(args["count"], "S"),
                lambda y: draw_glyph(x, y))),
        
        P().line(header.es).ep().fssw(-1, 0.75, 1),
        P().line([g.pnw, g.psw.project(-90, 70)]).ep().fssw(-1, 0.75, 1),
        P().line([g.psw.project(-180, 70), g.pse]).ep().fssw(-1, 0.75, 1),
        P().gridlines(g, args["count"]).fssw(-1, 0.75, 1),
        
        P().line([p:=horizontal.ambit().pe.project(0, 30), p2:=p.project(0, ln:=350)]).ep()
            .line([p2, p2.project(45*3, ad:=14)]).ep()
            .line([p2, p2.project(-45*3, ad)]).ep()
            .fssw(-1, 0, 2),

        P().line([p:=vertical.ambit().pn.project(90, 30), p2:=p.project(90, ln)]).ep()
            .line([p2, p2.project(45*-1, ad)]).ep()
            .line([p2, p2.project(45*5, ad)]).ep()
            .fssw(-1, 0, 2),
    ).data(fontPath=fnt.path))

    return out


#def build(_):
#    show_in_finder(chars_display.last_return.data("fontPath"))


def on_click(pos):
    for m in (dsview_display.last_return
        .find(lambda x: x.data("position") and pos.inside(x.ambit()))):
        variations = list([v[1] for v in m.data("font").variations().items()])
        range_0 = variations[a].get("maxValue") - (min:=variations[a].get("minValue"))
        pos_0 = int(m.data("position").get("x")*range_0 + min)
        range_1 = variations[b].get("maxValue") - (min:=variations[b].get("minValue"))
        pos_1 = int(m.data("position").get("y")*range_1 + min)
        print(f"Position: {variations[a].get("axisTag")} {pos_0}, {variations[b].get("axisTag")} {pos_1} / {variations[a].get("axisTag")} {m.data("position").get("x")}, {variations[b].get("axisTag")} {m.data("position").get("y")}")