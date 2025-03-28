from coldtype import *
from coldtype.blender import *

bt = BlenderTimeline(ººBLENDERºº, 120)

@b3d_runnable(playback=B3DPlayback.AlwaysStop)
def prerun(bw):
    bw.delete_previous()

@b3d_animation((1080, 1080), timeline=bt)
def sequence(f:Frame):
    current = bt.current(1, f.i)

    return (StSt(current.name, Font.JBMono(), 200
        , wght=current.e("eeo", 0))
        .align(f.a.r)
        .pen()
        .ch(b3d(lambda bp: bp
            .extrude(1))))