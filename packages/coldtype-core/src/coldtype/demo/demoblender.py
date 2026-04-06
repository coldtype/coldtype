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
            .align(f.a.r)
            .mapv(lambda i, p: p
                .ch(b3d(lambda bp: bp
                    .extrude(f.adj(-i*5)
                        .e("seio", 1, rng=(0.1, 1.75))))))))