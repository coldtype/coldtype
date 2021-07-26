from coldtype import *
from coldtype.blender import *
from coldtype.text.composer import Glyphwise

@b3d_animation(timeline=90, blender_file="examples/blender/coldtype.blend")
def coldtype2(f):
    return (StSt("COLD\nTYPE",
        Font.ColdtypeObviously(),
        font_size=550,
        ro=1,
        wdth=f.e("eeio", 1),
        leading=f.e("eeio", 1, rng=(20, 200)),
        tu=f.e("eeio", 1, rng=(0, 50)))
        .align(f.a.r)
        .index(0, lambda p: p.translate(f.e("eeio", 1, rng=(-20, 0)), 0))
        .index(1, lambda p: p.translate(f.e("eeio", 1, rng=(20, 0)), 0))
        .collapse()
        .pmap(lambda i, p: p
            .outline(f.e("eeio", 1, rng=(2, 5)))
            .f(hsl(0.65, 1))
            .tag(f"letter{i}")
            .ch(b3d("Text", lambda bp: bp
                .extrude(f.e("eeio", 1, rng=(3.5, 0.5)))
                .locate(0, f.e("l", 0, rng=(30, 0)), 0)
                .rotate(90, 0, 0)
                #.rotate(90, 0, 0)
                .with_origin((bp.dat.ambit().pc.x/100, 0, bp.dat.ambit().pc.y/100), lambda bp2: bp2.rotate(90-f.adj(-i).e("eeio", 0, rng=(0, 360), to1=False)))
                #.rotate(i*10)
                #.rotate(0)
                , material="letter"))))

build, release = coldtype2.build_release()