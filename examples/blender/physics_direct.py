from coldtype import *
from coldtype.blender import *

txt = "FALL\nING\nTEXT"

@b3d_runnable()
def setup(bpw:BpyWorld):
    (bpw.delete_previous()
        .timeline(Timeline(120), resetFrame=0)
        .rigidbody(speed=3, frame_end=1000))
    
    (BpyObj.Find("Plane")
        .rigidbody("passive", friction=1, bounce=0))
    
    (BpyGroup.Curves(
        StSt(txt, Font.MutatorSans(), 3
            , wght=1
            , leading=1)
            .map(lambda p: p.track_to_width(9))
            .deblank()
            .centerZero())
        .map(lambda bp: bp
            .extrude(0.275)
            .locate(z=10)
            .convert_to_mesh()
            .rigidbody(friction=0.5)))
