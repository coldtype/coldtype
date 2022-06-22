from coldtype import *
from coldtype.blender import *

# TODO tag the b3d lambda value as BlenderPen

# @b3d_runnable()
# def prerun(bw):
#     bw.deletePrevious()

@b3d_animation(timeline=60, denoise=0)
def varfont(f):
    return (StSt("T", Font.ColdtypeObviously(),
        fontSize=f.e("seio", 1, rng=(300, 1500)),
        wdth=f.e("seio", 1, rng=(1, 0)))
        .align(f.a.r)
        .f(1)
        .mapv(lambda p: p            
            .ch(b3d(lambda bp: bp
                .extrude(f.e("seio", 1, rng=(0.5, 5.75)))))))