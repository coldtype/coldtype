from coldtype.blender.util import *


def text_in_channel(se, c, sort=True):
    matches = []
    for s in se.sequences:
        if hasattr(s, "text") and s.channel == c:
            matches.append(s)
    if sort: 
        return sorted(matches, key=lambda s: s.frame_start)
    return matches

def next_neighbor(se, curr):
    candidates = text_in_channel(se, curr.channel)
    for c in candidates:
        if curr.frame_final_end == c.frame_start:
            return c


class TimedTextEditorOperator(bpy.types.Operator):
    bl_idname = "wm.timed_text_editor_operator"
    bl_label = "Timed Text Editor"
    
    timed_text: bpy.props.StringProperty(name="Text")
    bl_property = "timed_text"

    def execute(self, context):
        self.report({'INFO'}, self.timed_text)
        
        se = bpy.data.scenes[0].sequence_editor
        if hasattr(se.active_strip, "text"):
            se.active_strip.text = self.timed_text
            se.active_strip.name = self.timed_text.split(" ")[0]
        
        return {'FINISHED'}

    def invoke(self, context, event):
        se = bpy.data.scenes[0].sequence_editor
        self.timed_text = se.active_strip.text
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class TimedTextSplitter(bpy.types.Operator):
    bl_idname = "wm.timed_text_splitter"
    bl_label = "Timed Text Splitter"

    def execute(self, context):
        se = bpy.data.scenes[0].sequence_editor
        if hasattr(se.active_strip, "text"):
            next = next_neighbor(se, se.active_strip)
            if not next:
                print("ERROR NO NEXT")
                return {'FINISHED'}
            curr = se.active_strip
            txts = curr.text.split(" ")
            #print(curr.name, next.name, txts)
            curr.text = txts[0]
            next.text = " ".join(txts[1:])
            curr.name = txts[0]
            next.name = txts[1]
            curr.select = False
            next.select = True
            se.active_strip = next
            bpy.ops.sequencer.refresh_all()
        
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.ops.sequencer.split(type="SOFT",
            frame=bpy.data.scenes[0].frame_current,
            channel=bpy.data.scenes[0].sequence_editor.active_strip.channel,
            side="RIGHT")
        bpy.ops.sequencer.refresh_all()
        return self.execute(context)



class TimedTextSelector(bpy.types.Operator):
    bl_idname = "wm.timed_text_selector"
    bl_label = "Timed Text Selector"

    def invoke(self, context, event):
        se = bpy.data.scenes[0].sequence_editor
        fc = bpy.data.scenes[0].frame_current
        
        if hasattr(se.active_strip, "text"):
            curr = se.active_strip
            all = text_in_channel(se, curr.channel)
            next = None
            for s in all:
                if s.frame_start <= fc < s.frame_final_end:
                    next = s
            if next:
                curr.select = False
                next.select = True
                se.active_strip = next
                bpy.ops.sequencer.refresh_all()
        return {'FINISHED'}


class TimedTextRoller(bpy.types.Operator):
    bl_idname = "wm.timed_text_roller"
    bl_label = "Timed Text Roller"

    def invoke(self, context, event):
        se = bpy.data.scenes[0].sequence_editor
        fc = bpy.data.scenes[0].frame_current
        
        if hasattr(se.active_strip, "text"):
            curr = se.active_strip
            all = text_in_channel(se, curr.channel)
            next = None
            prev = None
            for s in all:
                s.select = False
                s.select_right_handle = False
                s.select_left_handle = False

                if fc == s.frame_start:
                    next = s
                if fc == s.frame_final_end:
                    prev = s
            
            if prev:
                prev.select = True
                prev.select_right_handle = True
            if next:
                next.select = True
                next.select_left_handle = True
                se.active_strip = next
            
            bpy.ops.sequencer.refresh_all()
        return {'FINISHED'}


class Coldtype2DImporter(bpy.types.Operator):
    """Import the current Coldtype animation as a PNG frame sequence in the Blender sequence editor"""

    bl_idname = "wm.coldtype_2d_importer"
    bl_label = "Coldtype 2D Importer"

    def invoke(self, context, event):
        from coldtype.blender import Action
        
        sq = find_sequence()
        if sq:
            bpy.ops.sequencer.image_strip_add(
                directory=str(sq.output_folder) + "/",
                files=[dict(name=str(p.output_path.name)) for p in sq.passes(Action.RenderAll, None)],
                relative_path=True,
                frame_start=0,
                frame_end=sq.duration-1,
                channel=2)
        
        bpy.ops.sequencer.refresh_all()
        return {'FINISHED'}


class Coldtype2DPrerender(bpy.types.Operator):
    """Enable to draw prerendered frames to live preview Image Editor image"""

    bl_idname = "wm.coldtype_2d_prerendered"
    bl_label = "Coldtype 2D Prerender"

    def execute(self, context):
        current = bpy.app.driver_namespace.get("_coldtype_prerendered", False)
        bpy.app.driver_namespace["_coldtype_prerendered"] = not current
        bpy.app.driver_namespace["_coldtype_needs_rerender"] = True
        return {'FINISHED'}


class Coldtype2DSequenceDefaults(bpy.types.Operator):
    """Some good defaults for editing and rendering a 2D sequence based on PNG images"""

    bl_idname = "wm.coldtype_2d_sequence_defaults"
    bl_label = "Coldtype 2D Sequence Defaults"

    def execute(self, context):
        context.scene.render.use_compositing = False
        context.scene.render.use_sequencer = True
        context.scene.use_audio_scrub = True
        context.scene.view_settings.view_transform = "Standard"
        return {'FINISHED'}


class Coldtype2DRenderOne(bpy.types.Operator):
    """Render the current frame with the Coldtype renderer"""

    bl_idname = "wm.coldtype_2d_render_one"
    bl_label = "Coldtype 2D Render One"

    def execute(self, _):
        print("EXTERNAL RENDER ONE")
        remote("render_index", [bpy.data.scenes[0].frame_current])
        return {'FINISHED'}

class Coldtype2DRenderWorkarea(bpy.types.Operator):
    """Render the current workarea with the Coldtype renderer; if not workarea is set, this will render the entire animation"""

    bl_idname = "wm.coldtype_2d_render_workarea"
    bl_label = "Coldtype 2D Render Workarea"

    def execute(self, _):
        print("RENDER WORKAREA")
        remote("render_workarea")
        return {'FINISHED'}

class Coldtype2DRenderAll(bpy.types.Operator):
    """Render the entire animation with the Coldtype renderer"""

    bl_idname = "wm.coldtype_2d_render_all"
    bl_label = "Coldtype 2D Render All"

    def execute(self, _):
        print("RENDER ALL")
        remote("render_all")
        return {'FINISHED'}

class Coldtype2DSetWorkarea(bpy.types.Operator):
    """Set a workarea based on the current frame and the text data in the sequence"""

    bl_idname = "wm.coldtype_2d_set_workarea"
    bl_label = "Coldtype 2D Set Workarea"

    def execute(self, context):
        sq = find_sequence()
        if sq:
            fc = context.scene.frame_current
            work = sq.t.findWordsWorkarea(fc)
            if work:
                start, end = work
                context.scene.frame_start = start
                context.scene.frame_end = end-1
            else:
                context.scene.frame_start = 0
                context.scene.frame_end = sq.t.duration-1
        
        return {'FINISHED'}

class Coldtype2DUnsetWorkarea(bpy.types.Operator):
    """Set the workarea to the entire length of the animation"""

    bl_idname = "wm.coldtype_2d_unset_workarea"
    bl_label = "Coldtype 2D Unset Workarea"

    def execute(self, context):
        sq = find_sequence()
        if sq:
            context.scene.frame_start = 0
            context.scene.frame_end = sq.t.duration-1
        return {'FINISHED'}

class Coldtype2DOpenInEditor(bpy.types.Operator):
    """Open the current Coldtype source file in your configured text editor"""

    bl_idname = "wm.coldtype_2d_open_in_editor"
    bl_label = "Coldtype 2D Open-in-editor"

    def execute(self, _):
        remote("open_in_editor")
        return {'FINISHED'}


class COLDTYPE_2D_PT_Panel(bpy.types.Panel):
    bl_idname = 'COLDTYPE_2D_PT_panel'
    bl_label = 'Coldtype 2D'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        prerendered = bpy.app.driver_namespace.get("_coldtype_prerendered", False)

        layout = self.layout
        layout.operator(Coldtype2DSequenceDefaults.bl_idname, text="Set Defaults", icon="SETTINGS",)
        layout.operator(Coldtype2DImporter.bl_idname, text="Import Frames", icon="DOCUMENTS",)
        layout.separator()
        layout.operator(Coldtype2DPrerender.bl_idname, text="Prerender Enabled" if prerendered else "Prerender Disabled", icon="TEXTURE_DATA",)
        layout.operator(Coldtype2DRenderOne.bl_idname, text="Render One", icon="IMAGE_DATA",)
        layout.operator(Coldtype2DRenderWorkarea.bl_idname, text="Render Workarea", icon="RENDERLAYERS",)
        layout.operator(Coldtype2DRenderAll.bl_idname, text="Render All", icon="RENDER_ANIMATION",)
        layout.separator()
        layout.operator(Coldtype2DSetWorkarea.bl_idname, text="Set Workarea", icon="STICKY_UVS_VERT",)
        layout.operator(Coldtype2DUnsetWorkarea.bl_idname, text="Unset Workarea", icon="STICKY_UVS_LOC",)
        layout.separator()
        layout.operator(Coldtype2DOpenInEditor.bl_idname, text="Open in Editor", icon="SCRIPT",)


addon_keymaps = []

def register():
    bpy.utils.register_class(TimedTextEditorOperator)
    bpy.utils.register_class(TimedTextSplitter)
    bpy.utils.register_class(TimedTextSelector)
    bpy.utils.register_class(TimedTextRoller)
    
    bpy.utils.register_class(Coldtype2DPrerender)
    bpy.utils.register_class(Coldtype2DSequenceDefaults)
    bpy.utils.register_class(Coldtype2DImporter)
    bpy.utils.register_class(Coldtype2DRenderOne)
    bpy.utils.register_class(Coldtype2DRenderWorkarea)
    bpy.utils.register_class(Coldtype2DRenderAll)
    bpy.utils.register_class(Coldtype2DSetWorkarea)
    bpy.utils.register_class(Coldtype2DUnsetWorkarea)
    bpy.utils.register_class(Coldtype2DOpenInEditor)
    
    bpy.utils.register_class(COLDTYPE_2D_PT_Panel)
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:
        addon_keymaps.append([
            km:=kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR'),
            km.keymap_items.new("wm.timed_text_editor_operator", type='T', value='PRESS', shift=True)
        ])
        addon_keymaps.append([
            km:=kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR'),
            km.keymap_items.new("wm.timed_text_splitter", type='V', value='PRESS', shift=True)
        ])
        addon_keymaps.append([
            km:=kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR'),
            km.keymap_items.new("wm.timed_text_selector", type='D', value='PRESS')
        ])
        addon_keymaps.append([
            km:=kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR'),
            km.keymap_items.new("wm.timed_text_roller", type='F', value='PRESS')
        ])
        addon_keymaps.append([
            km:=kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR'),
            km.keymap_items.new(Coldtype2DImporter.bl_idname, type='I', value='PRESS', shift=True)
        ])
        addon_keymaps.append([
            km:=kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR'),
            km.keymap_items.new(Coldtype2DRenderOne.bl_idname, type='R', value='PRESS')
        ])
        addon_keymaps.append([
            km:=kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR'),
            km.keymap_items.new(Coldtype2DRenderWorkarea.bl_idname, type='R', value='PRESS', shift=True)
        ])
        addon_keymaps.append([
            km:=kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR'),
            km.keymap_items.new(Coldtype2DRenderAll.bl_idname, type='R', value='PRESS', shift=True, oskey=True)
        ])
        addon_keymaps.append([
            km:=kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR'),
            km.keymap_items.new(Coldtype2DOpenInEditor.bl_idname, type='O', value='PRESS')
        ])
        addon_keymaps.append([
            km:=kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR'),
            km.keymap_items.new(Coldtype2DSetWorkarea.bl_idname, type='W', value='PRESS', shift=True)
        ])
        addon_keymaps.append([
            km:=kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR'),
            km.keymap_items.new(Coldtype2DUnsetWorkarea.bl_idname, type='W', value='PRESS', shift=True, oskey=True)
        ])
 
 
def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    
    addon_keymaps.clear()
    bpy.utils.unregister_class(TimedTextEditorOperator)


def add_2d_panel():
    register()