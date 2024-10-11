from coldtype import *

author = "Josef Müller-Brockmann"
publisher = "Niggli"

txt_en = [
    "Grid systems",
    "in graphic design",
    "A visual communcation manual\nfor graphic designers,\ntypographers and\nthree dimensional designers"
]

txt_de = [
    "Raster systeme",
    "für die\nvisuelle Gestaltung",
    "Ein Handbuch für\nGrafiker, Typografen und\nAusstellungsgestalter"
]

@renderable(Rect(215*5, 300*5), bg=hsl(0.015, 0.6, 0.555))
def cover(r):
    s = Scaffold(r.inset(40)).labeled_grid(4, 8, 30, 30)
    s1 = Style("GrossV", 160, wght=0.55, wdth=0.91)
    s2 = Style("GrossV", 37, wght=0.25, wdth=0.91)
    return (P(
        s.borders().fssw(-1, 1, 0.5),
        P(s).fssw(-1, 1, 0.25),
        s.view(fill=False, vectors=True).f(bw(1, 0.25)) if 1 else None,
        P(
            StSt(author, s2).f(0).align(s["a2"], "NW"),
            StSt(txt_en[0], s1).align(s["c0"], "NW"),
            StSt(txt_en[1], s2).align(s["d0"], "NW"),
            StSt(txt_en[2], s2).align(s["d2"], "NW"),
            StSt(txt_de[0], s1).align(s["e0"], "NW"),
            StSt(txt_de[1], s2).align(s["f0"], "NW"),
            StSt(txt_de[2], s2).align(s["f2"], "NW"),
            StSt(publisher, s2).align(s["h2"], "SW", ty=1)
        ).f(0)))