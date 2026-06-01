from coldtype import *
from coldtype.tool import Tool, fmt_path
from coldtype.osutil import show_in_finder


tool = Tool(ººinputsºº, dict(
    font=[Font.MutatorSans(), str, None, "Font search string"],
    text=["A", str, None, "Text to display"],
    count=[9, int, None, "How many cells in x and y dimensions"],
    axes=["0,1", str, None, "Which axes to display"],
    )
    , ui=ººuiºº
    , name="Designspace Viewer")


A, B = [int(x) for x in tool.state["axes"].split(",")]
a, b = A, B


@animation(Rect(tool.state["rect"].w, tool.state["rect"].h+(h:=120)), bg=1, tl=Timeline(len(tool.state["fonts"])))
def dsview_display(f):
    global a, b

    fnt:Font = tool.state["fonts"][f.i]
    path = fnt.fmtpath

    variations = fnt.variations()
    axes = list(variations.keys())
    variations = list(variations.items())

    if len(axes) == 1:
        a, b = 0, 0
    else:
        a, b = A, B

    l = Scaffold(f.a.r).cssgrid("85 a", f"{h} a 85", "h h / a2 g / x a1")

    def draw_glyph(x, y):
        r = y.el.inset(4)
        return (P(
            StSt(tool.state["text"], fnt, tool.state["fontSize"], variations={axes[a]:x.e, axes[b]:y.e})
                .align(r)
                .f(0)
                .data(font=fnt, position=dict(x=x.e, y=y.e))))

    return (P(
        P(l["h"].r).f(1),
        StSt(fnt.family, Font.JBMono(), 40, wght=1).align(l["h"].r.inset(25), "NE").f(0),
        StSt(path, Font.JBMono(), 22, wght=0.25).align(l["h"].r.inset(25), "SE").f(0),
        
        horizontal:=StSt(fnt.getName(variations[a][1].get("axisNameID")) + f" : “{variations[a][0]}” ", Font.JBMono(), 24, wght=1)
            .align(l["a1"].r, "W")
            .f(0)
            .t(d:=100, 0),
        vertical:=StSt(fnt.getName(variations[b][1].get("axisNameID")) + f" : “{variations[b][0]}” ", Font.JBMono(), 24, wght=1)
            .rotate(90)
            .unframe()
            .align(l["a2"], "S")
            .t(0, d)
            .f(0),
            
        P().enumerate((g:=l["g"].r).subdivide(tool.state["count"], "W"),
            lambda x: P().enumerate(x.el.subdivide(tool.state["count"], "S"),
                lambda y: draw_glyph(x, y))),
        
        P().line(l["h"].r.es).ep().fssw(-1, 0.75, 1),
        P().line(l["a2+x"].r.ee).ep().fssw(-1, 0.75, 1),
        P().line(l["a1+x"].r.en).ep().fssw(-1, 0.75, 1),
        
        P().gridlines(g, tool.state["count"]).fssw(-1, 0.75, 1),

        StSt(str(int(variations[a][1].get("minValue"))), Font.JBMono(), 20, wght=1).align(l["a1"].r, "W").t(d:=20, 0).f(fill:=bw(0.65)),
        StSt(str(int(variations[a][1].get("maxValue"))), Font.JBMono(), 20, wght=1).align(l["a1"].r, "E").t(-d, 0).f(fill),

        StSt(str(int(variations[b][1].get("minValue"))), Font.JBMono(), 20, wght=1).align(l["a2"].r, "S").t(0, d).f(fill),
        StSt(str(int(variations[b][1].get("maxValue"))), Font.JBMono(), 20, wght=1).align(l["a2"].r, "N").t(0, -d).f(fill),
        
        P().line([p:=horizontal.ambit().pe.project(0, 30), p2:=p.project(0, ln:=350)]).ep()
            .line([p2, p2.project(45*3, ad:=14)]).ep()
            .line([p2, p2.project(-45*3, ad)]).ep()
            .fssw(-1, 0, 2),

        P().line([p:=vertical.ambit().pn.project(90, 30), p2:=p.project(90, ln)]).ep()
            .line([p2, p2.project(45*-1, ad)]).ep()
            .line([p2, p2.project(45*5, ad)]).ep()
            .fssw(-1, 0, 2),
    ).data(fontPath=fnt.path))


def build(_):
    show_in_finder(dsview_display.last_return[1].data("fontPath"))


def on_click(pos):
    for m in (dsview_display.last_return.find(lambda x: x.data("position") and pos.inside(x.ambit()))):
        variations = list([v[1] for v in m.data("font").variations().items()])
        range_0 = variations[a].get("maxValue") - (min:=variations[a].get("minValue"))
        pos_0 = int(m.data("position").get("x")*range_0 + min)
        range_1 = variations[b].get("maxValue") - (min:=variations[b].get("minValue"))
        pos_1 = int(m.data("position").get("y")*range_1 + min)
        print(f"Position: {variations[a].get("axisTag")} {pos_0}, {variations[b].get("axisTag")} {pos_1} / {variations[a].get("axisTag")} {m.data("position").get("x")}, {variations[b].get("axisTag")} {m.data("position").get("y")}")