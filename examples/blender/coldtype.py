from coldtype import *
from coldtype.blender import *

@b3d_animation(timeline=90,
    blend=__sibling__("coldtype2.blend"))
def coldtype5(f):
    return (StSt("COLD\nTYPE",
        Font.ColdtypeObviously(),
        font_size=550,
        ro=1,
        wdth=f.e("eeio", 1),
        leading=f.e("eeio", 1, rng=(20, 200)),
        tu=f.e("eeio", 1, rng=(200, 50)),
        rotate=f.e("ceio", 1, rng=(5, 0)))
        .align(f.a.r)
        .index(0, lambda p: p
            .translate(f.e("eeio", 1, rng=(-20, 0)), 0))
        .index(1, lambda p: p
            .translate(f.e("eeio", 1, rng=(20, 0)), 0))
        .collapse()
        .pmap(lambda i, p: p
            #.outline(f.e("eeio", 1, rng=(2, 5)))
            .f(hsl(0.65, 1))
            .tag(f"letter{i}")
            .ch(b3d("Text", lambda bp: bp
                .extrude(f.e("seio", 1, rng=(2.5, 0.25)))
                .locate(0, f.e("ceo", 0, rng=(30, 0)), 0)
                .rotate(90, 0, 0)
                .with_origin((bp.dat.ambit().pc.x/100, 0, bp.dat.ambit().pc.y/100), lambda bp2: bp2
                    .rotate(90, f.adj(-i).e("eeio", 0, rng=(0, 360), to1=False), f.adj(-i).e("ceio", 0, rng=(0, 360), to1=False)))))))