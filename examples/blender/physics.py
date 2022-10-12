from coldtype import *
from coldtype.blender import *

txt = "FALL\nING\nABC"

@b3d_runnable()
def setup(bw:BpyWorld):
    with (bw
        .deletePrevious()
        .timeline(Timeline(120))
        .rigidbody(speed=1.5, frame_end=1000)):
        (BpyObj.Find("Plane")
            .rigidbody("passive", friction=1, bounce=0))

@b3d_renderable(reset_to_zero=1)
def justi(r):
    return (StSt(txt,
        Font.MutatorSans(), 300, wght=1)
        .track(110, v=1)
        .map(lambda p: p.trackToRect(r.inset(70)))
        .align(r.inset(50))
        .deblank()
        .pmap(lambda p: p
            .ch(b3d(lambda bp: bp
                .extrude(0.275)
                .convertToMesh()
                .rigidbody(friction=0.5),
                dn=True,
                zero=True))
            .ch(b3d_post(lambda bp: bp
                .locate_relative(z=30)))))
