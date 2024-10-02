from coldtype import *
from coldtype.blender import *

@b3d_runnable(playback=B3DPlayback.KeepPlaying)
def prerun(bw:BpyWorld):
    bw.delete_previous(materials=False)

@b3d_animation(timeline=60, center=(0, 1), upright=1)
def varfont2(f):
    return (P(
        Glyphwise("COLD\nTYPE", lambda g:
            Style(Font.ColdtypeObviously(), 375
                , wdth=f.adj(-g.i*5).e("seio", 1, rng=(0.98, 0))))
            .xalign(f.a.r)
            .track(50, v=1)
            .align(f.a.r.drop(100, "S"))
            .mapv(lambda i, p: p
                .ch(b3d(lambda bp: bp
                    .extrude(f.adj(-i*5)
                        .e("seio", 1,
                            rng=(0.1, 1.75)))))),
        StSt("Now in 3D!", Font.RecursiveMono(), 100)
            .align(f.a.r.take(0.2, "S"))
            .pen()
            .f(hsl(0.65, f.e("eeio", 1), 0.6))
            .ch(b3d(lambda bp: bp
                .extrude(f.e("eeio", 1, rng=(0.1, 3)))
                .specular(0)
                .roughness(1)
                .metallic(f.e("eeio", 1))
                , material="auto"))
            .hide()
            ))