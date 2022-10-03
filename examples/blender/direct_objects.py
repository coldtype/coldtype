from coldtype import *
from coldtype.blender import *

@b3d_runnable()
def setup(blw:BpyWorld):
    (blw.deletePrevious("Coldtype"
            , materials=True)
        .deletePrevious("Cubes"
            , materials=True)
        .timeline(Timeline(120)
            , resetFrame=0
            , output=__FILE__
            , version=1))
    
    with blw.rigidbody(2.1, 120):
        (BpyObj.Empty("Empty1"))
        
        (BpyObj.Curve("ObviGlyph")
            .draw(StSt("TYPE", Font.ColdObvi(), 5)
                .centerZero())
            .extrude(0.2)
            .locate(z=7.5)
            .rotate(x=90)
            .convertToMesh()
            .rigidbody("active", bounce=0.5)
            .material("coldtype_material"))
        
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

        (BpyObj.Monkey()
            .locate(z=11)
            .rotate(z=45)
            .scale(1,1,1)
            .rigidbody("active", bounce=0.3)
            .material("monkey_material")
            .subsurface()
            .shadeSmooth())
        
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
            .shadeSmooth())
        
        (BpyObj.Plane()
            .scale(x=30, y=30)
            .applyScale()
            .rigidbody("passive", bounce=0.5)
            .material("plane_material", lambda m: m
                .f(hsl(0.17, 0.8, 0.5))
                .specular(0)))