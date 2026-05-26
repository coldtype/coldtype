from coldtype import *
from coldtype.tool import parse_inputs, print_font_results
from coldtype.blender import *
from coldtype.blender.util import remote

# coldtype-embedded-profile b3dlo

"""
A classic 5-by-5 Noordzij Cube, displaying any
variable font with three axes

(https://letterror.com/articles/noordzij-cube.html)
"""

def parse_inputs(inputs, defaults, ui=True, positional=True, name="Coldtype", blender_ui=False):
    if ui is not None and ui is not False:
        defaults["rect"] = [
            Rect(1080, 1080),
            lambda xs: Rect([int(x) for x in str(xs).split(",")])]

        defaults["preview_only"] = [False, bool]
        defaults["log"] = [False, bool]

    parsed = {}
    if not isinstance(inputs, dict):
        for idx, input in enumerate(inputs):
            if "=" in input:
                k, v = input.split("=")
                parsed[k] = v
            elif input in defaults.keys():
                parsed[input] = True
            elif positional:
                try:
                    parsed[list(defaults.keys())[idx]] = input
                except KeyError:
                    pass
    else:
        parsed = {**inputs}

    out = {}
    font_variations = {}
    out["font_variations"] = {}

    for k, v in defaults.items():
        if k in ["w", "h"]:
            out[k] = v
            defaults[k] = [v, int]
        if k == "font" and v[0] is not None:
            out[k] = v[0]
            out["fonts"] = [v][0]
            out["font_variations"] = v[0].variations()
            out["fontSize"] = 42
        else:
            out[k] = v[0]
            if k not in parsed and len(v) > 2:
                raise Exception(v[2])
    
    for k, v in parsed.items():
        if k in defaults:
            if defaults[k][0] is None and v is None:
                pass
            else:
                if isinstance(v, str):
                    if k == "font":
                        sized = v.split(":")
                        if len(sized) > 1:
                            out["fontSize"] = int(sized[1])
                        else:
                            out["fontSize"] = 72
                        
                        v = sized[0]
                        vs = v.split("@")
                        fnt_idx = 0
                        if len(vs) > 1:
                            fnt_idx = int(vs[1])
                        
                        fonts = Font.ListAll(vs[0])
                        if len(fonts) == 0:
                            print(f"\n\n‼️ Search \"{v}\" returned no fonts ‼️\n")
                            out[k] = Font.ColdtypeObviously()
                        else:
                            out["fonts"] = fonts
                            print_font_results(fonts, fnt_idx)
                            out[k] = fonts[fnt_idx]
                            font_variations = out[k].variations()
                    elif k == "rect":
                        if v == "max":
                            out[k] = ui.get("monitor").scale(2).inset(200).square().zero()
                        else:
                            out[k] = eval(f"Rect({v})")
                        #raise Exception("IMPLEMENT MAX with screen size")
                    elif defaults[k][1] == bool:
                        out[k] = bool(eval(v))
                    else:
                        out[k] = defaults[k][1](v)
                else:
                    if k == "rect":
                        print("ALSO HERE")
                        out[k] = Rect(v)
                    else:
                        out[k] = v
        else:
            if k in font_variations:
                out["font_variations"][k] = float(v)
            else:
                print(f"> key {k} not recognized")

    if blender_ui:
        try:
            import bpy, bpy.props
            from bpy.types import Panel, PropertyGroup

            def on_change(self, context):
                props = context.scene.coldtype_tool_props
                for k in annotations.keys():
                    args[k] = getattr(props, k)
                setup.func(BpyWorld().deselect_all())

            annotations = {}
            
            for k, v in defaults.items():
                if k not in ["font", "rect", "preview_only", "log"]:
                    value = out[k]
                    field_type = defaults[k][1]
                    if field_type == str:
                        annotations[k] = bpy.props.StringProperty(name=k, description="N/A", default=value, update=on_change)
                    elif field_type == int:
                        annotations[k] = bpy.props.IntProperty(name=k, description="N/A", default=value, update=on_change)
            
            Properties = type(
                "ColdtypeToolProperties",
                (PropertyGroup,),
                { "__annotations__": annotations })

            class VIEW3D_PT_coldtypetool(Panel):
                bl_label = name
                bl_idname = f"VIEW3D_PT_{name}"
                bl_space_type = "VIEW_3D"
                bl_region_type = "UI"
                bl_category = "Tool"
            
                def draw(self, context):
                    layout = self.layout
                    props = context.scene.coldtype_tool_props
                    for k, v in annotations.items():
                        layout.prop(props, k, text=k)

            classes = (Properties, VIEW3D_PT_coldtypetool)
            
            def register():
                for cls in classes:
                    bpy.utils.register_class(cls)
                bpy.types.Scene.coldtype_tool_props = bpy.props.PointerProperty(type=Properties)
            
            # def unregister():
            #     del bpy.types.Scene.coldtype_tool_props
            #     for cls in reversed(classes):
            #         bpy.utils.unregister_class(cls)

            # try:
            #     unregister()
            # except Exception as e:
            #     print(e)
            
            register()

        except Exception as e:
            print(e)

    return out


args = parse_inputs(ººinputsºº, dict(
    font=[Font.MutatorSans(), str],
    text=["A", str],
    count=[3, int],
    )
    , ui=ººuiºº
    , blender_ui=True)


@b3d_runnable()
def setup(bpw:BpyWorld):
    d = args["count"]

    BpyObj.Find("Cube").delete()
    BpyObj.Find("Plane").delete()

    (bpw.delete_previous()
        .cycles(128)
        .timeline(Timeline(240)
            , resetFrame=0
            , output=setup.output_folder / "noord1_"))
    
    pivot = (BpyObj.Empty("Center")
        .locate(x=(d-1)/2, y=(d-1)/2, z=0)
        .insert_keyframes("rotation_euler",
            (0, lambda bp: bp.rotate()),
            (240, lambda bp: bp.rotate(z=360)))
        .make_keyframes_linear("rotation_euler"))
    
    (BpyObj.Find("Camera").parent(pivot))
    
    def add_glyph(x, y, z):
        (BpyObj.Curve(f"Glyph_{x}_{y}_{z}")
            .draw(StSt(args["text"], args["font"], 0.5
                , slnt=x/(d-1)
                , wdth=(y/(d-1))
                , wght=1-((z/(d-1))))
                .centerZero()
                .pen())
            .rotate(x=90)
            .locate(x=x, y=y, z=z)
            .extrude(0.1)
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