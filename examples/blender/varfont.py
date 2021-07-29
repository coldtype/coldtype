from coldtype import *
from coldtype.blender import *

fnt = Font.Find("SwearCilatiVariable")

@b3d_animation(timeline=60)
def varfont(f):
    return (Glyphwise("Vary", lambda g:
        Style(fnt, 475,
            opsz=f.adj(-g.i*5).e("seio", 1, rng=(0.98, 0)),
            wght=f.adj(-g.i*15).e("seio", 1, rng=(0.98, 0))))
        .align(f.a.r)
        .pmap(lambda i,p: p.tag(f"L{i}")
            .chain(b3d("Text", lambda bp: bp
                .extrude(f.adj(-i*5)
                    .e("ceio", 1, rng=(0.5, 1.75)))))))