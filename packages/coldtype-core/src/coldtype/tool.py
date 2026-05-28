from pathlib import Path
from dataclasses import dataclass
from subprocess import run

from coldtype.geometry.rect import Rect
from coldtype.text.font import Font
from coldtype.blender import b3d_runnable


try:
    import bpy, bpy.props # type: ignore
    from bpy.types import Panel, PropertyGroup # type: ignore
    from bpy_extras.io_utils import ImportHelper # type: ignore
    from coldtype.blender import BpyWorld
    has_bpy = True
except ImportError:
    has_bpy = False


def fmt_path(path: Path) -> str:
    try:
        return "~/" + str(path.relative_to(Path.home()))
    except ValueError:
        return str(path)


def print_font_results(results, selected=None):
    maxsys = max([len(f.system_name) for f in results])
    maxpat = max([len(fmt_path(f.path)) for f in results])
    print("")
    print(f"     # {'Name':<{maxsys}} Path")
    print(f"   {'-'*(maxsys+maxpat+7)}")
    for idx, result in enumerate(results):
        if idx == selected:
            print(f"➡️  {idx:>{3}} {result.system_name:<{maxsys}} {fmt_path(result.path)}")
        else:
            print(f"   {idx:>{3}} {result.system_name:<{maxsys}} {fmt_path(result.path)}")
    print("\n")


def open_in_font_goggles(fonts:list[Font]):
    return run(["open", "-a", "FontGoggles", *[f.path for f in fonts]])


@dataclass
class Tool:
    inputs: dict
    defaults: dict
    name: str = "Coldtype"
    doc: str = None
    ui: bool = True
    positional: bool = True
    print_fonts: bool = True
    blender_runnable: b3d_runnable = None
    state: dict = lambda: {}

    def __post_init__(self):
        if self.ui is not None and self.ui is not False:
            self.defaults["rect"] = [
                Rect(1080, 1080),
                lambda xs: Rect([int(x) for x in str(xs).split(",")]), None, "Rectangle for viewer window"]

            #self.defaults["preview_only"] = [False, bool]
            #Aself.defaults["log"] = [False, bool]

        parsed = {}
        if not isinstance(self.inputs, dict):
            for idx, input in enumerate(self.inputs):
                if "=" in input:
                    k, v = input.split("=")
                    if k in self.defaults:
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

        if not has_bpy:
            print(f"\n⚙️  {self.name}")
            if self.doc:
                print(f"  {self.doc}\n")
            #else:
            #    print("")
            print("\n🛠️  Command-Line Arguments  🛠️\n")

        for k, v in self.defaults.items():
            try:
                default_value, var_type, missing_exception, docstring = v
            except Exception as e:
                print(k)
                raise e

            if not has_bpy and k not in ["rect"]:
                print(f"  • {k}")
                print(f"    Default: {default_value}")
                print(f"      Doc: {docstring}")

            if k in ["w", "h"]:
                out[k] = v
                self.defaults[k] = [v, int]
            if k == "font" and default_value is not None:
                out[k] = default_value
                out["fonts"] = default_value
                out["font_variations"] = default_value.variations()
                out["fontSize"] = 42
            else:
                out[k] = default_value
                if k not in parsed and missing_exception is not None:
                    raise Exception(missing_exception)
        
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
                                if not has_bpy and self.print_fonts:
                                    print_font_results(fonts, fnt_idx)
                                out[k] = fonts[fnt_idx]
                                font_variations = out[k].variations()
                        elif k == "rect":
                            if v == "max":
                                out[k] = self.ui.get("monitor").scale(2).inset(200).square().zero()
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

        if self.blender_runnable:
            self.add_blender()


    def add_blender(self):
        if not has_bpy:
            return

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
            self.blender_runnable.func(BpyWorld().deselect_all())

        annotations = {}
        
        for k, v in self.defaults.items():
            if k not in ["rect", "preview_only", "log"]:
                value = self.state[k]
                field_type = self.defaults[k][1]
                docstring = self.defaults[k][-1]
                if k == "font":
                    annotations[k] = bpy.props.StringProperty(name=k, description=docstring, default=str(value.path), update=on_change)
                elif field_type == str:
                    annotations[k] = bpy.props.StringProperty(name=k, description=docstring, default=value, update=debounced_update)
                elif field_type == int:
                    annotations[k] = bpy.props.IntProperty(name=k, description=docstring, default=value, update=debounced_update)
                elif field_type == float:
                    annotations[k] = bpy.props.FloatProperty(name=k, description=docstring, default=value, update=debounced_update)
        
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
            bl_label = self.name
            bl_idname = f"VIEW3D_PT_{self.name}"
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
                        layout.separator(factor=1.0, type='LINE')
                        row = layout.row()
                        row.label(text=f"Dir: {fmt_path(Path(getattr(props, k)).parent)}")
                        row = layout.row()
                        row.label(text=f"Font: {Path(getattr(props, k)).name}")
                        font = Font.Cacheable(getattr(props, k))
                        if variations := font.variations():
                            row = layout.row()
                            row.label(text=f"Variations: {",".join(list(variations.keys()))}")
                        layout.separator(factor=1.0, type='LINE')
                    else:
                        layout.prop(props, k, text=k)

        classes = (Properties, WM_OT_ColdtypeChooseFont, VIEW3D_PT_coldtypetool)
        
        for cls in classes: bpy.utils.register_class(cls)
        
        bpy.types.Scene.coldtype_tool_props = bpy.props.PointerProperty(type=Properties)

        if hasattr(bpy.context.scene, "coldtype_tool_props"):
            props = bpy.context.scene.coldtype_tool_props
            for k in annotations.keys():
                self.state[k] = getattr(props, k)


def parse_inputs(inputs, defaults, ui=True, positional=True):
    return Tool(inputs, defaults, name="Coldtype", ui=ui, positional=positional).state