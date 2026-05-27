from coldtype import *
from coldtype.tool import parse_inputs, print_font_results, fmt_path
from coldtype.blender import *
from coldtype.blender.util import remote

# coldtype-embedded-profile b3dlo

"""
A classic 5-by-5 Noordzij Cube, displaying any
variable font with three axes

(https://letterror.com/articles/noordzij-cube.html)
"""

from dataclasses import dataclass

@dataclass
class Tool:
    inputs: dict
    defaults: dict
    name: str = "Coldtype"
    ui: bool = True
    positional: bool = True
    blender_ui: bool = False
    state: dict = lambda: {}

    def __post_init__(self):
        if self.ui is not None and self.ui is not False:
            self.defaults["rect"] = [
                Rect(1080, 1080),
                lambda xs: Rect([int(x) for x in str(xs).split(",")])]

            self.defaults["preview_only"] = [False, bool]
            self.defaults["log"] = [False, bool]

        parsed = {}
        if not isinstance(self.inputs, dict):
            for idx, input in enumerate(self.inputs):
                if "=" in input:
                    k, v = input.split("=")
                    parsed[k] = v
                elif input in self.defaults.keys():
                    parsed[input] = True
                elif self.positional:
                    try:
                        parsed[list(self.defaults.keys())[idx]] = input
                    except KeyError:
                        pass
        else:
            parsed = {**self.inputs}

        out = {}
        font_variations = {}
        out["font_variations"] = {}

        for k, v in self.defaults.items():
            if k in ["w", "h"]:
                out[k] = v
                self.defaults[k] = [v, int]
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
            if k in self.defaults:
                if self.defaults[k][0] is None and v is None:
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
                        elif self.defaults[k][1] == bool:
                            out[k] = bool(eval(v))
                        else:
                            out[k] = self.defaults[k][1](v)
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

        self.state = out

        if self.blender_ui:
            try:
                import bpy, bpy.props # type: ignore
                from bpy.types import Panel, PropertyGroup # type: ignore
                from bpy_extras.io_utils import ImportHelper # type: ignore

                _pending_updates = {}
                _pending_updates[1] = None

                DEBOUNCE_DELAY = 0.25

                def _do_expensive_update():
                    on_change(None, None)
                    _pending_updates[1] = None
                    return None

                def debounced_update(x, y):
                    if _pending_updates[1] is not None:
                        try:
                            bpy.app.timers.unregister(_pending_updates[1])
                        except ValueError:
                            pass  # already fired
        
                    def timer_fn(): return _do_expensive_update()
                    
                    _pending_updates[1] = timer_fn
                    bpy.app.timers.register(timer_fn, first_interval=DEBOUNCE_DELAY)

                def on_change(x, y):
                    props = bpy.context.scene.coldtype_tool_props
                    for k in annotations.keys():
                        self.state[k] = getattr(props, k)
                    setup.func(BpyWorld().deselect_all())

                annotations = {}
                
                for k, v in self.defaults.items():
                    if k not in ["rect", "preview_only", "log"]:
                        value = out[k]
                        field_type = self.defaults[k][1]
                        if k == "font":
                            annotations[k] = bpy.props.StringProperty(name=k, description="N/A", default=str(value.path), update=on_change)
                        elif field_type == str:
                            annotations[k] = bpy.props.StringProperty(name=k, description="N/A", default=value, update=debounced_update)
                        elif field_type == int:
                            annotations[k] = bpy.props.IntProperty(name=k, description="N/A", default=value, update=debounced_update)
                        elif field_type == float:
                            annotations[k] = bpy.props.FloatProperty(name=k, description="N/A", default=value, update=debounced_update)
                
                Properties = type(
                    "ColdtypeToolProperties",
                    (PropertyGroup,),
                    { "__annotations__": annotations })
                
                class WM_OT_ColdtypeChooseFont(bpy.types.Operator, ImportHelper):
                    """Open file dialog to pick a font"""
                    
                    bl_idname = "wm.coldtype_choose_font"
                    bl_label = "Choose font file"
                    bl_options = {"REGISTER","UNDO"}
                    
                    filter_glob: bpy.props.StringProperty(
                        default='*.ttf;*.otf;*.ufo;*.designspace',
                        options={'HIDDEN'}) # type: ignore

                    def invoke(self, context, event):
                        context.window_manager.fileselect_add(self)
                        return {'RUNNING_MODAL'}

                    def execute(self, context):
                        # TODO check if font has at least 3 axes
                        path = Path(self.filepath)
                        props = context.scene.coldtype_tool_props
                        setattr(props, "font", str(path))
                        on_change(None, context)
                        return {'FINISHED'}

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
                            if k == "font":
                                row = layout.row()
                                row.operator("wm.coldtype_choose_font", text="", icon="FONTPREVIEW")
                                row.label(text="Browse for a font file")
                                row = layout.row()
                                row.label(text=f"Dir: {fmt_path(Path(getattr(props, k)).parent)}")
                                row = layout.row()
                                row.label(text=f"Font: {Path(getattr(props, k)).name}")
                            else:
                                layout.prop(props, k, text=k)

                classes = (Properties, WM_OT_ColdtypeChooseFont, VIEW3D_PT_coldtypetool)
                
                for cls in classes: bpy.utils.register_class(cls)
                
                bpy.types.Scene.coldtype_tool_props = bpy.props.PointerProperty(type=Properties)

                if hasattr(bpy.context.scene, "coldtype_tool_props"):
                    props = bpy.context.scene.coldtype_tool_props
                    for k in annotations.keys():
                        self.state[k] = getattr(props, k)

            except Exception as e:
                print(">>>", e)

        return self


t = Tool(ººinputsºº, dict(
    font=[Font.MutatorSans(), str],
    text=["A", str],
    count=[3, int],
    fontScale=[0.5, float],
    extrude=[0.1, float])
    , ui=ººuiºº
    , blender_ui=True)


@b3d_runnable()
def setup(bpw:BpyWorld):
    d = t.state["count"]

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
            .draw(StSt(t.state["text"]
                , t.state["font"]
                , t.state["fontScale"]
                , slnt=x/(d-1)
                , wdth=(y/(d-1))
                , wght=1-((z/(d-1))))
                .centerZero()
                .pen())
            .rotate(x=90)
            .locate(x=x, y=y, z=z)
            .extrude(t.state["extrude"])
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