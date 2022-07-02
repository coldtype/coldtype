from coldtype import *
from coldtype.blender import *

@b3d_runnable(playback=0)
def setup(blw:BpyWorld):
    print(">>", __FILE__)

    (blw.deletePrevious("Coldtype"
            , materials=False)
        .deletePrevious("Cubes"
            , materials=False)
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

        (BpyObj.Monkey()
            .locate(z=11)
            .rotate(z=45)
            .scale(1,1,1)
            .rigidbody("active", bounce=0.3)
            .material("monkey_material")
            .subsurface()
            .shadeSmooth())
        
        (BpyObj.UVSphere("Cube1", collection="Cubes")
            .scale(2, 2, 2)
            .locate(z=20)
            .rigidbody("active", bounce=0.3)
            .material("cube_material")
            .subsurface()
            .shadeSmooth())
        
        (BpyObj.Plane()
            .scale(x=20, y=20)
            .applyScale()
            .rigidbody("passive", bounce=0.5)
            .material("plane_material"))