from coldtype import *
from coldtype.blender import *

"""
Here there is no simultaneous 2D/3D; we're just using
Coldtype to script Blender directly

(i.e. this script only works when Blender is running)
"""

@b3d_runnable()
def setup(blw:BpyWorld):
    (blw.delete_previous("Coldtype"
            , materials=True)
        .delete_previous("Cubes"
            , materials=True)
        .timeline(Timeline(120)
            , resetFrame=0
            , output=setup.output_folder / "do1_"
            , version=1))
    
    blw.rigidbody(1.5, 120)

    (BpyObj.Empty("Empty1"))
    
    (BpyObj.Curve("ObviGlyph")
        .draw(StSt("TYPE", Font.ColdObvi(), 5)
            .centerZero())
        .extrude(0.2)
        .locate(z=7.5)
        .rotate(x=90)
        .convert_to_mesh()
        .rigidbody("active", bounce=0.5)
        .material("coldtype_material")
        .shade_flat())
    
    (BpyGroup.Curves(
        StSt("COLD", Font.MuSan(), 3
            , wght=1, wdth=1)
            .centerZero()
        , collection="/Glyphs")
        .map(lambda bp: bp
            .parent("Empty1")
            .extrude(0.25)
            .locate(z=15)
            .convertToMesh()
            .rigidbody("active", bounce=0.5)
            .material("coldtype_material")))
    
    BpyObj.Find("Empty1").locate(z=-2)

    (BpyMaterial.Find("monkey_material")
        .f(hsl(0.3, 1))
        .roughness(1)
        .specular(0))

    monkey = (BpyObj.Monkey()
        .locate(z=11)
        .rotate(z=45)
        .scale(1,1,1)
        .rigidbody("active", bounce=0.3)
        .material("monkey_material")
        .subsurface()
        .shade_smooth())
    
    monkey.copy().locate(x=6)
    monkey.copy().locate(x=-6)
    
    (BpyMaterial.Find("monkey_material")
        .f(hsl(0.6, 1)))
    
    (BpyObj.UVSphere("Cube1", collection="Cubes")
        .scale(2, 2, 2)
        .locate(z=20)
        .rigidbody("active", bounce=0.3)
        .material("cube_material", lambda m: m
            .f(hsl(0.85, 1))
            .transmission(1))
        .subsurface()
        .shade_smooth())
    
    (BpyObj.Plane()
        .scale(x=30, y=30)
        .apply_scale()
        .rigidbody("passive", bounce=0.5)
        .material("plane_material", lambda m: m
            .f(hsl(0.17, 0.8, 0.5))
            .specular(0)))