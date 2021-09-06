import bpy, json
from pathlib import Path

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


class TimedTextImporter(bpy.types.Operator):
    bl_idname = "wm.timed_text_importer"
    bl_label = "Timed Text Importer"

    def invoke(self, context, event):
        from coldtype.blender import b3d_sequencer, Action
        
        rs = bpy.app.driver_namespace.get("_coldtypes", [])
        sq = None
        for r in rs:
            if isinstance(r, b3d_sequencer):
                sq = r
        
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


def remote(command):
    (Path("~/.coldtype/command.json")
        .expanduser()
        .write_text(json.dumps(dict(action=command if isinstance(command, str) else command.value))))


class ColdtypeRenderOne(bpy.types.Operator):
    bl_idname = "wm.coldtype_render_one"
    bl_label = "Coldtype Render One"

    def execute(self, _):
        print("RENDER ONE")
        remote("render_one")
        return {'FINISHED'}

class ColdtypeRenderWorkarea(bpy.types.Operator):
    bl_idname = "wm.coldtype_render_workarea"
    bl_label = "Coldtype Render Workarea"

    def execute(self, _):
        print("RENDER WORKAREA")
        remote("render_workarea")
        return {'FINISHED'}

class ColdtypeRenderAll(bpy.types.Operator):
    bl_idname = "wm.coldtype_render_all"
    bl_label = "Coldtype Render All"

    def execute(self, _):
        print("RENDER ALL")
        remote("render_all")
        return {'FINISHED'}


class COLDTYPE_PT_Panel(bpy.types.Panel):
    bl_idname = 'COLDTYPE_PT_panel'
    bl_label = 'Coldtype'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tool'
 
    def draw(self, context):
        layout = self.layout
        #layout.operator('wm.timed_text_renderer', text='Render One').action = 'RENDER_ONE'
        #layout.operator('wm.timed_text_renderer', text='Render Workarea').action = 'RENDER_WORKAREA'
        #layout.operator('wm.timed_text_renderer', text='Render All').action = 'RENDER_ALL'
        layout.operator(ColdtypeRenderOne.bl_idname, text="Render One", icon="RENDER_ANIMATION", )
        layout.operator(ColdtypeRenderWorkarea.bl_idname, text="Render Workarea", icon="RENDER_ANIMATION", )
        layout.operator(ColdtypeRenderAll.bl_idname, text="Render All", icon="RENDER_ANIMATION", )


# class TimedTextRenderer(bpy.types.Operator):
#     bl_idname = "wm.timed_text_renderer"
#     bl_label = "Timed Text Renderer"
    
#     action: bpy.props.EnumProperty(
#         items=[
#             ('RENDER_ONE', 'Render One', 'Render One'),
#             ('RENDER_WORKAREA', 'Render Workarea', 'Render Workarea'),
#             ('RENDER_ALL', 'Render All', 'Render All'),
#         ]
#     )

#     def execute(self, context):
#         if self.action == "RENDER_ONE":
#             print("RENDER ONE!")
#         return {'FINISHED'}

#     def invoke(self, context, event):
#         wm = context.window_manager
#         return wm.invoke_props_dialog(self)


addon_keymaps = []


def register(testing=False):
    bpy.utils.register_class(TimedTextEditorOperator)
    bpy.utils.register_class(TimedTextSplitter)
    bpy.utils.register_class(TimedTextSelector)
    bpy.utils.register_class(TimedTextImporter)
    
    bpy.utils.register_class(ColdtypeRenderOne)
    bpy.utils.register_class(ColdtypeRenderWorkarea)
    bpy.utils.register_class(ColdtypeRenderAll)
    bpy.utils.register_class(COLDTYPE_PT_Panel)
    
    if testing:
        bpy.ops.wm.timed_text_splitter('EXEC_DEFAULT')
        #bpy.ops.wm.timed_text_editor_operator('INVOKE_DEFAULT')
        return
    
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
            km.keymap_items.new("wm.timed_text_importer", type='I', value='PRESS', shift=True)
        ])
        addon_keymaps.append([
            km:=kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR'),
            km.keymap_items.new(ColdtypeRenderOne.bl_idname, type='R', value='PRESS')
        ])
 
 
def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    
    addon_keymaps.clear()
    bpy.utils.unregister_class(TimedTextEditorOperator)


def add_shortcuts():
    register(testing=False)

if __name__ == "__main__":
    register(testing=0)