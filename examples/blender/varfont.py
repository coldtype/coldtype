from coldtype import *
from coldtype.blender import *

@b3d_animation(timeline=60, denoise=0)
def varfont(f):
    return (Glyphwise("TYPE", lambda g:
        Style(Font.ColdtypeObviously(), 475,
            wdth=f.adj(-g.i*5).e("seio", 1, rng=(0.98, 0))))
        .align(f.a.r)
        .f(1)
        .pmap(lambda i, p: p
            .ch(b3d(lambda bp: bp
                .extrude(f.adj(-i*5)
                    .e("ceio", 1, rng=(0.5, 1.75)))))))