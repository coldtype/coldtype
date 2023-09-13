from coldtype import *
from coldtype.blender import *

"""
A 3D Physics simulation that uses lo-res polygons to do the actual physics, then uses copied, hi-res bezier curves (parented to the lo-res polygons) to display
"""

txt = "COLD\nTYPE"

@b3d_runnable()
def setup(bpw:BpyWorld):
    (bpw.delete_previous()
        .timeline(Timeline(150), resetFrame=0
            , output=setup.output_folder / "ct1_")
        .cycles(128)
        .rigidbody(speed=2, frame_end=150))
    
    (BpyObj.Plane("Field")
        .rigidbody("passive", friction=1, bounce=0)
        .dimensions(x=160, y=130)
        .material("field_mat", lambda m: m
            .f(0)
            .specular(0)
            .roughness(1)))

    lockup = (StSt(txt, Font.ColdObvi(), 7, wdth=0.5, leading=1)
        .map(lambda p: p.track_to_width(13))
        .centerZero()
        .translate(0, 6)
        .deblank()
        .collapse())
    
    lores = (BpyGroup.Curves(lockup, "Letter_Lores")
        .map(lambda idx, bp: bp
            .extrude(0.5)
            .with_temp_origin((0, 0, 0), lambda bp: bp
                .rotate(x=90))))

    hires = lores.copy("Letter_Hires")

    lores.map(lambda bp: bp
        .convert_to_mesh()
        .remesh(3)
        .apply_modifier("Remesh")
        .rigidbody(friction=1, bounce=0.5))
    
    hires.map(lambda idx, bp: bp
        .parent(f"Letter_Lores_{idx}", hide=True)
        .material("letter_mat", lambda m: m
            .f(1)))