from coldtype import *
from coldtype.blender import *
from coldtype.fx.skia import phototype

txt = [
    "bauhausbücher",
    "moholy-nagy",
    "von\nmaterial\nzu\narchitektur",
]

r = Rect("letter").scale(2)

@renderable(r, bg=hsl(0), render_bg=0)
def cover(r):
    s = Scaffold(r.inset(100*2, 110*2))
    s1 = Style("GrossV", 60*2, wdth=1, wght=0.75)
    txts = (P(
        StSt(txt[0], s1).f(1)
            .align(s, "NE"),
        StSt(txt[1], s1.mod(fontSize=51*2)).f(0)
            .align(s, "W")
            .t(0, 10),
        StSt(txt[2], s1.mod(fontSize=82*2)).f(0)
            .align(s, "SW")))
    
    number = (P(Rect(87*2, 984))
        .layer(
            lambda p: p.layer(
                1,
                lambda p: p.copy()
                    .scale(1, 1)
                    .skew(0.45, 0)
                    .align(p.ambit(), "NE")
                    .drop(130*2, "S"),
                lambda p: p.copy()
                    .take(p.w, "S")
                    .scale(2.75, 1)
                    .t(-40*2, 130*2)),
            lambda p: p.layer(
                1,
                lambda p: p.copy()
                    .scale(1.1, 1)
                    .skew(0.60, 0)
                    .align(p.ambit(), "NE")
                    .take(p.w*1.85, "E")))
        .map(lambda p: p.pen(frame=False).ro())
        .reverse()
        .spread(-67*2, zero=True)
        .xor()
        .f(0)
        .print()
        .layer(1, lambda p: P().enumerate(p.ambit().subdivide_with_leading(60, 14, "N"), lambda x: P(x.el.o(0, 1))).pen())
        .intersection()
        .f(1)
        .align(s.r, "NE")
        .t(0, 77)
        #.f(0)
        .ch(phototype(r, 0.5, 130, 30, fill=bw(0)))
        )
    
    return P(number, txts)

@b3d_runnable(force_refresh=1)
def setup(blw:BpyWorld):
    blw.delete_previous(materials=False)

    (BpyObj.Plane("GlassPlate")
        .scale(4, r.aspect()*4)
        .rotate(x=85)
        .solidify(0.0005)
        .locate_relative(y=0.001)
        .material("glass_plate_material"))

    (BpyObj.Plane("Glass")
        .scale(4, r.aspect()*4)
        .rotate(x=85)
        .material("glass_material", lambda m: m
            .f(0)
            .specular(0)
            .image(cover.pass_path(0))))