"""
Noordzij cube, to show 3 axes of font at once
Can specify -wght to reverse order of axis in axesOrder field
"""

from coldtype import *
from coldtype.tool import Tool
from coldtype.blender import *

# coldtype-embedded-profile b3dlo


"""
ala (https://letterror.com/articles/noordzij-cube.html)
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
    
    BpyObj.Find("Camera").parent(pivot)

    font = Font.Cacheable(tool.state["font"])
    vars = font.variations()
    vars_keys = list(vars.keys())
    
    axes_order = tool.state.get("axesOrder")
    if axes_order == "auto":
        axes_order = vars_keys
    else:
        axes_order = [x.strip() for x in axes_order.split(",")]
        vars_keys = [x.replace("-", "") for x in axes_order]
    
    def add_glyph(x, y, z):
        variations = {}
        for idx, dim in enumerate([x, y, z]):
            v = dim/(d-1)
            if axes_order[idx].startswith("-"):
                variations[vars_keys[idx]] = 1-v
            else:
                variations[vars_keys[idx]] = v

        (BpyObj.Curve(f"Glyph_{x}_{y}_{z}")
            .draw(StSt(tool.state["text"]
                , tool.state["font"]
                , tool.state["fontScale"]
                , variations=variations)
                .centerZero()
                .pen()
                .cond(tool.state["outline"] > 0,
                    lambda p: p.removeOverlap().outline(tool.state["outline"]/1000)))
            .rotate(x=90)
            .locate(x=x, y=y, z=z)
            .extrude(tool.state["extrude"])
            .convert_to_mesh()
            .material(f"letter_mat_{y}", lambda m: m
                .f(1)
                #.f(hsl(y/(d+1), 1, 0.5))
                .specular(0)
                .roughness(1)))
    
    for z in range(0, d):
        for y in range(0, d):
            for x in range(0, d):
                add_glyph(x, y, z)



tool = Tool(ººinputsºº, dict(
    font=[Font.MutatorSans(), str],
    text=["a", str],
    axesOrder=["auto", str],
    count=[3, int],
    fontScale=[0.5, float],
    extrude=[0.02, float],
    outline=[0, int],)
    , ui=ººuiºº
    , blender_runnable=setup)
