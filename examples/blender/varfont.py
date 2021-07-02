from coldtype import *
from coldtype.blender import b3d, b3d_animation
from coldtype.text.composer import Glyphwise

fnt = Font.Cacheable("~/Type/fonts/fonts/SwearCilatiVariable.ttf")

@b3d_animation(timeline=60)
def varfont(f):
    return (Glyphwise("Variable", lambda i,c:
        Style(fnt, 325,
            opsz=f.adj(-i*5).e("seio", 1, rng=(0.98, 0)),
            wght=f.adj(-i*15).e("seio", 1, rng=(0.98, 0))
            ))
        .align(f.a.r)
        .pmap(lambda i,p: p.tag(f"L{i}")
            .chain(b3d("Text", lambda bp: bp
                .metallic(0)
                .extrude(f.adj(-i*5)
                    .e("ceio", 1, rng=(0.015, 3)))))))