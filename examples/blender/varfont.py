from coldtype import *
from coldtype.blender import *

@b3d_animation(timeline=60, denoise=0)
def varfont(f):
    return (StSt("COLD", Font.ColdtypeObviously(),
        fontSize=f.e("seio", 1, rng=(300, 500)),
        wdth=f.e("seio", 1, rng=(1, 0)))
        .align(f.a.r)
        .pen()
        .f(1)
        .ch(b3d(lambda bp: bp
            .extrude(f.e("seio", 1, rng=(0.5, 5.75))))))