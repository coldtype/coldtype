from coldtype import *
from coldtype.blender import *

@b3d_runnable(playback=B3DPlayback.KeepPlaying)
def prerun(bw):
    bw.delete_previous()

@b3d_animation(timeline=60, denoise=0)
def varfont(f):
    return (StSt("COLD\nTYPE", Font.ColdtypeObviously()
        , fontSize=f.e("seio", 1, rng=(300, 500))
        , wdth=f.e("seio", 1, rng=(1, 0)))
        .align(f.a.r)
        .f(1)
        .mapv(lambda p: p
            .ch(b3d(lambda bp: bp
                .extrude(f.e("seio", 1, rng=(0.5, 5.75)))))))