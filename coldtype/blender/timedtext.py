import bpy


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

        se = bpy.data.scenes[0].sequence_editor
        fc = bpy.data.scenes[0].frame_current
        
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
                channel=3)
        
        bpy.ops.sequencer.refresh_all()
        return {'FINISHED'}


addon_keymaps = []


def register(testing=False):
    bpy.utils.register_class(TimedTextEditorOperator)
    bpy.utils.register_class(TimedTextSplitter)
    bpy.utils.register_class(TimedTextSelector)
    bpy.utils.register_class(TimedTextImporter)
    
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
            km.keymap_items.new("wm.timed_text_importer", type='I', value='PRESS')
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