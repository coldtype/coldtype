from coldtype import *
from coldtype.blender import b3d, b3d_animation
from coldtype.text.composer import Glyphwise

fnt = Font.Cacheable("~/Type/fonts/fonts/Ehrie-V0_1-VF.ttf")
fnt = Font.Cacheable("~/Type/fonts/fonts/NaNJauneMaxi-Var.ttf")

@b3d_animation(timeline=60)
def varfont(f):
    return (Glyphwise("Vari", lambda i,c:
        Style(fnt, 350,
            diss=f.adj(-i*5).e("seio", 1, rng=(0.98, 0)),
            wght=f.adj(-i*5).e("seio", 1)))
        .align(f.a.r)
        .pmap(lambda i,p: p
            .tag(f"L{i}")
            .ch(b3d("Text", lambda bp: bp
                .extrude(f.adj(-i*5)
                    .e("ceio", 1, rng=(0.015, 3)))))))