from coldtype import *
from coldtype.tool import Tool
from coldtype.blender import *

# coldtype-embedded-profile b3dlo

"""
A classic 5-by-5 Noordzij Cube, displaying any
variable font with three axes

(https://letterror.com/articles/noordzij-cube.html)
"""


@b3d_runnable()
def setup(bpw:BpyWorld):
    d = tool.state["count"]

    BpyObj.Find("Cube").delete()
    BpyObj.Find("Plane").delete()

    (bpw.delete_previous()
        .cycles(128)
        .timeline(Timeline(240)
            , resetFrame=0
            , output=setup.output_folder / "noord1_"))
    
    pivot = (BpyObj.Empty("Center")
        .locate(x=0, y=0, z=0)
        .insert_keyframes("rotation_euler",
            (0, lambda bp: bp.rotate()),
            (240, lambda bp: bp.rotate(z=360)))
        .make_keyframes_linear("rotation_euler"))
    
    (BpyObj.Find("Camera").parent(pivot))
    
    def add_glyph(x, y, z):
        (BpyObj.Curve(f"Glyph_{x}_{y}_{z}")
            .draw(StSt(tool.state["text"]
                , tool.state["font"]
                , tool.state["fontScale"]
                , slnt=x/(d-1)
                , wdth=(y/(d-1))
                , wght=1-((z/(d-1))))
                .centerZero()
                .pen())
            .rotate(x=90)
            .locate(x=x, y=y, z=z)
            .extrude(tool.state["extrude"])
            .convert_to_mesh()
            .material(f"letter_mat_{y}", lambda m: m
                .f(1)
                #.f(hsl(y/(d+1), 1, 0.8))
                .specular(0)
                .roughness(1)))
    
    for z in range(0, d):
        for y in range(0, d):
            for x in range(0, d):
                add_glyph(x, y, z)



tool = Tool(ººinputsºº, dict(
    font=[Font.MutatorSans(), str],
    text=["A", str],
    count=[3, int],
    fontScale=[0.5, float],
    extrude=[0.1, float])
    , ui=ººuiºº
    , blender_runnable=setup)
