from coldtype.blender.timedtext import Coldtype2DPrerender
from coldtype.blender.util import *


class Coldtype3DPrerender(bpy.types.Operator):
    """Enable to draw prerendered frames to live preview Image Editor image"""

    bl_idname = "wm.coldtype_3d_prerendered"
    bl_label = "Coldtype 3D Prerender"

    def execute(self, context):
        current = bpy.app.driver_namespace.get("_coldtype_prerendered", False)
        bpy.app.driver_namespace["_coldtype_prerendered"] = not current
        bpy.app.driver_namespace["_coldtype_needs_rerender"] = True
        return {'FINISHED'}


class Coldtype3DRenderOne(bpy.types.Operator):
    """Render the current frame via Coldtype with the offline Blender renderer"""

    bl_idname = "wm.coldtype_3d_render_one"
    bl_label = "Coldtype 3D Render One"

    def execute(self, _):
        print("RENDER ONE")
        remote("render_index", [bpy.data.scenes[0].frame_current])
        return {'FINISHED'}


class Coldtype3DRenderAll(bpy.types.Operator):
    """Render all frames via Coldtype with the offline Blender renderer"""

    bl_idname = "wm.coldtype_3d_render_all"
    bl_label = "Coldtype 3D Render All"

    def execute(self, _):
        print("RENDER ALL")
        remote("render_all", [bpy.data.scenes[0].frame_current])
        return {'FINISHED'}


class Coldtype3DOpenInEditor(bpy.types.Operator):
    """Open the current Coldtype source file in your configured text editor"""

    bl_idname = "wm.coldtype_3d_open_in_editor"
    bl_label = "Coldtype 3D Open-in-editor"

    def execute(self, _):
        remote("open_in_editor")
        return {'FINISHED'}

class Coldtype3DShowInFinder(bpy.types.Operator):
    """Open the current Coldtype source file in the file browser"""

    bl_idname = "wm.coldtype_3d_show_in_finder"
    bl_label = "Coldtype 3D Show-in-finder"

    def execute(self, _):
        remote("show_in_finder")
        return {'FINISHED'}


class COLDTYPE_3D_PT_Panel(bpy.types.Panel):
    bl_idname = 'COLDTYPE_3D_PT_panel'
    bl_label = 'Coldtype 3D'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        prerendered = bpy.app.driver_namespace.get("_coldtype_prerendered", False)

        layout = self.layout
        layout.operator(Coldtype3DRenderOne.bl_idname, text="Render One", icon="IMAGE_DATA",)
        layout.operator(Coldtype3DRenderAll.bl_idname, text="Render All", icon="RENDER_ANIMATION",)
        #layout.operator(Coldtype3DPrerender.bl_idname, text="Prerender Enabled" if prerendered else "Prerender Disabled", icon="TEXTURE_DATA",)
        layout.separator()
        layout.operator(Coldtype3DOpenInEditor.bl_idname, text="Open in Editor", icon="SCRIPT",)
        layout.operator(Coldtype3DShowInFinder.bl_idname, text="Show in Finder", icon="FILEBROWSER",)

addon_keymaps = []

def register():
    bpy.utils.register_class(Coldtype3DPrerender)
    bpy.utils.register_class(Coldtype3DRenderOne)
    bpy.utils.register_class(Coldtype3DRenderAll)
    bpy.utils.register_class(Coldtype3DOpenInEditor)
    bpy.utils.register_class(Coldtype3DShowInFinder)
    
    bpy.utils.register_class(COLDTYPE_3D_PT_Panel)
 
 
def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    
    addon_keymaps.clear()
    bpy.utils.unregister_class(COLDTYPE_3D_PT_Panel)


def add_3d_panel():
    register()