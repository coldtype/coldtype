import bpy, traceback, json
from pathlib import Path
from collections import defaultdict

from coldtype.renderer.reader import SourceReader
from coldtype.blender import b3d_animation, walk_to_b3d
from coldtype.blender.timedtext import add_shortcuts


def persist_sequence(last_persisted):
    channels = defaultdict(lambda: [])

    scene = bpy.data.scenes[0]
    for s in scene.sequence_editor.sequences:
        channels[s.channel].append(s)
    
    tracks = []
    for c, clips in channels.items():
        track = dict(index=c)
        _clips = []
        for clip in clips:
            if hasattr(clip, "text"):
                _clips.append(dict(
                    name=clip.name,
                    text=clip.text,
                    start=clip.frame_start,
                    end=clip.frame_final_end))
        track["clips"] = sorted(_clips, key=lambda c: c["start"])
        if len(_clips) > 0:
            tracks.append(track)
    
    if len(tracks) == 0:
        return None
    
    jpath = str(Path(bpy.data.filepath)) + ".json"
    out = dict(
        start=scene.frame_start,
        end=scene.frame_end,
        current_frame=scene.frame_current,
        tracks=tracks)
    
    if out == last_persisted:
        return out
    else:
        #print("NEW CHANGES")
        Path(jpath).write_text(json.dumps(out, indent=4))
        for r in bpy.app.driver_namespace.get("_coldtypes", []):
            if hasattr(r, "reread_timeline"):
                r.reread_timeline()
        return out
    

def render_as_image(r, res):
    from coldtype.pens.skiapen import SkiaPen
    import skia

    pimg = SkiaPen.Precompose(res, r.rect, disk=False)

    if r.name not in bpy.data.images.keys():
        bpy.data.images.new(r.name, width=r.rect.w, height=r.rect.h, alpha=True, float_buffer=True)

    img = bpy.data.images[r.name]
    img.pixels = pimg.toarray(colorType=skia.ColorType.kRGBA_F32_ColorType).ravel()

# original idea: https://blender.stackexchange.com/questions/15670/send-instructions-to-blender-from-external-application

class ColdtypeWatchingOperator(bpy.types.Operator):
    bl_idname = "wm.coldtype_watching_operator"
    bl_label = "Coldtype Watching Operator"

    _timer = None
    file = None
    sr = None
    current_frame = -1
    persisted = None

    def render_current_frame(self, statics=False):
        animation_found = False

        cfs = [r"^b3d_.*$"]
        if not statics:
            cfs = [r"^b3d_animation$"]
        
        out = []
        
        for r, res in self.sr.frame_results(
            self.current_frame,
            class_filters=cfs
            ):

            out.append(r)

            if isinstance(r, b3d_animation):
                if r.bake:
                    if statics:
                        walk_to_b3d(r.baked_frames(), renderable=r)
                else:
                    animation_found = True
                    if r.renderer == "b3d":
                        walk_to_b3d(res, renderable=r)
                    elif r.renderer == "skia":
                        #render_as_image(r, res)
                        pass
                    else:
                        raise Exception("r.renderer not supported", r.renderer)

            elif statics:
                walk_to_b3d(res, renderable=r)
                bpy.data.scenes[0].frame_set(0)
        
        #if not animation_found:
        #    bpy.data.scenes[0].frame_set(0)

        if statics:
            bpy.app.driver_namespace["_coldtypes"] = out
        return animation_found

    def reimport(self, arg):
        try:
            self.sr = SourceReader(arg)
            self.sr.unlink()
            #bpy.data.scenes[0].frame_start = 0

            bpy.app.handlers.frame_change_pre.clear()

            self.current_frame = bpy.context.scene.frame_current
            animation_found = self.render_current_frame(statics=True)
            
            if not animation_found:
                return

            def _frame_update_handler(scene):
                if scene.frame_current != self.current_frame:
                    self.current_frame = scene.frame_current
                    self.render_current_frame(statics=False)
            
            bpy.app.handlers.frame_change_pre.append(_frame_update_handler)
        
        except Exception as e:
            self.current_frame = -1
            bpy.app.handlers.frame_change_pre.clear()
            stack = traceback.format_exc()
            print("---"*10)
            print(stack)
        
        print(f"ran {arg}")

    def modal(self, context, event):
        if event.type == 'TIMER':
            if not bpy.context.screen.is_animation_playing:
                self.persisted = persist_sequence(self.persisted)

            if not self.file.exists():
                return {'PASS_THROUGH'}
            
            for line in self.file.read_text().splitlines():
                line = line.rstrip("\n")
                cmd, arg = line.split(",")
                if cmd == 'import':
                    self.reimport(arg)
                elif cmd == "play_preview":
                    bpy.ops.screen.animation_play()
                elif cmd == "frame_offset":
                    bpy.ops.screen.frame_offset(delta=int(arg))
                elif cmd == "refresh_sequencer":
                    bpy.ops.sequencer.refresh_all()
                elif cmd == 'cancel':
                    self.cancel(context)
                else:
                    print('unknown request=%s arg=%s' % (cmd,arg))
            
            if self.file.exists():
                self.file.unlink()

        return {'PASS_THROUGH'}

    def execute(self, context):
        ccf = bpy.app.driver_namespace.get("_coldtype_command_file")
        self.file = Path(ccf)
        print(">>>>>>>>>>>>", self.file)

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.25, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        print('timer removed')

def register_watcher():
    bpy.utils.register_class(ColdtypeWatchingOperator)

def unregister_watcher():
    bpy.utils.unregister_class(ColdtypeWatchingOperator)

def watch(command_file):
    bpy.app.driver_namespace["_coldtype_command_file"] = command_file
    
    register_watcher()
    bpy.ops.wm.coldtype_watching_operator()
    add_shortcuts()
    print("...waiting for coldtype...")