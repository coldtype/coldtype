from coldtype import *
from coldtype.blender import *

txt = "FALL\nING\nTEXT"

@b3d_runnable()
def setup(bw:BpyWorld):
    with (bw
        .deletePrevious()
        .timeline(Timeline(120))
        .rigidbody(speed=3.5, frame_end=1000)):
        (BpyObj.Find("Plane")
            .rigidbody("passive", friction=1, bounce=0))

@b3d_renderable(reset_to_zero=1)
def justi(r):
    return (StSt(txt,
        Font.MutatorSans(), 300, wght=0.25)
        .track(110, v=1)
        .map(λ.trackToRect(r.inset(70)))
        .align(r.inset(50))
        .remove_blanks()
        .pmap(lambda p: p
            .ch(b3d(lambda bp: bp
                .extrude(0.275)
                .convertToMesh()
                .rigidbody(friction=0.5),
                dn=True,
                zero=True))))
