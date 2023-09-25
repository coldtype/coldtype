from coldtype import *
from coldtype.blender import *

@b3d_runnable()
def setup(bpw:BpyWorld):
    bpw.delete_previous()

    (BpyObj.Cube("Cube")
        .dimensions(x=0.5, y=0.5, z=0.5)
        .arrayX(10, constant=1, relative=None)
        .apply_modifier("Array")
        .arrayZ(10, constant=1, relative=None)
        .apply_modifier("Array")
        .separate_by_loose_parts()
        .map(lambda bp: bp.origin_to_geometry()))