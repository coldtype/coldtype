from coldtype import *

@renderable(Rect(215*5, 300*5), bg=hsl(0.015, 0.55, 0.525))
def cover(r):
    s = Scaffold(r.inset(40)).labeled_grid(4, 8, 30, 30)
    return (P(
        s.borders().fssw(-1, 1, 0.5),
        P(s).fssw(-1, 1, 0.25),
        #s.view(fill=False, vectors=True).f(bw(1, 0.25)),
        StSt("Josef Müller-Brockmann", s2:=Style("GrossV", 37, wght=0.25, wdth=0.91))
            .f(0).align(s["a2"], "NW"),
        StSt("Grid systems", s1:=Style("GrossV", 160, wght=0.55, wdth=0.91))
            .f(0).align(s["c0"], "NW"),
        StSt("in graphic design", s2)
            .f(0).align(s["d0"], "NW"),
        StSt("A visual communcation manual\nfor graphic designers,\ntypographers and\nthree dimensional designers", s2)
            .f(0).align(s["d2"], "NW"),
        StSt("Raster systeme", s1)
            .f(0).align(s["e0"], "NW"),
        StSt("für die\nvisuelle Gestaltung", s2)
            .f(0).align(s["f0"], "NW"),
        StSt("Ein Handbuch für\nGrafiker, Typografen und\nAusstellungsgestalter", s2)
            .f(0).align(s["f2"], "NW"),
        StSt("Niggli", s2)
            .f(0).align(s["h2"], "SW", ty=1)
        ))