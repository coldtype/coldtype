from coldtype import *
from coldtype.blender import *

"""
Some text falls from on high
(using Blender directly via @b3d_runnable)
"""

txt = "FALL\nING\nTEXT"

@b3d_runnable()
def setup(bpw:BpyWorld):
    (bpw.delete_previous()
        .timeline(Timeline(90), resetFrame=0
            , output=setup.output_folder / "ft1_")
        .rigidbody(speed=3, frame_end=1000))
    
    (BpyObj.Find("Plane")
        .rigidbody("passive", friction=1, bounce=0)
        .material("floor_mat1", lambda m: m
            .f(1)
            .specular(1)
            .roughness(0.25)))
    
    (BpyGroup.Curves(
        StSt(txt, Font.MutatorSans(), 3
            , wght=1
            , leading=1)
            .map(lambda p: p.track_to_width(9))
            .deblank()
            .centerZero())
        .map(lambda bp: bp
            .extrude(0.275)
            .locate(z=30)
            .convert_to_mesh()
            .rigidbody(friction=0.5)
            .material("letter_mat1", lambda m: m
                .f(hsl(0.07, 1, 0.5))
                .roughness(1)
                .specular(0))))
