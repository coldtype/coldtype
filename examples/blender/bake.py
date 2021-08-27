from coldtype import *
from coldtype.blender import *

@b3d_animation(timeline=60, bake=True)
def baketest2(f):
    return (StSt("AV", Font.MutatorSans(), 200,
        wdth=f.e("eeio", 1),
        wght=f.e("eeio", 2),
        ro=1)
        .align(f.a.r, tv=1)
        .pmap(lambda p: p
            .ch(b3d(lambda bp: bp
                .rotate(90)
                .extrude(f.e("seio", 1, rng=(0.1, 1.5)))
                , material="letters"))))