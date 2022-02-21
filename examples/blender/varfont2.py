from coldtype import *
from coldtype.blender import *

@b3d_animation(timeline=60, center=(0, 1), upright=1)
def varfont2(f):
    ct = (Glyphwise("COLD\nTYPE", lambda g:
        Style(Font.ColdtypeObviously(), 375,
            wdth=f.adj(-g.i*5).e("seio", 1, rng=(0.98, 0))))
        .xalign(f.a.r)
        .track(50, v=1)
        .align(f.a.r.drop(100, "S"))
        .pmap(lambda i, p: p
            .ch(b3d(lambda bp: bp
                .extrude(f.adj(-i*5)
                    .e("seio", 1,
                        rng=(0.1, 1.75)))))))
    
    three = (StSt("IN 3D", "Peshka", 100
            , wght=f.e("eeio", loops:=1, rng=(1, 0))
            , wdth=f.e("eeio", loops, rng=(0, 1)))
        .align(f.a.r.take(0.2, "S"))
        .pen()
        .ch(b3d(lambda bp: bp
            .extrude(f.e("eeio", loops, rng=(0.1, 1))))))
    
    return P(ct, three)