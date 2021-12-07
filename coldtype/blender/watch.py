import bpy, traceback, json
from pathlib import Path
from collections import defaultdict
from coldtype.renderable.animation import animation

from coldtype.renderer.reader import SourceReader
from coldtype.blender import b3d_animation, b3d_runnable, walk_to_b3d
from coldtype.blender.timedtext import add_external_panel
from coldtype.blender.internal_panel import add_internal_panel
from coldtype.blender.util import remote

# def draw_png():
#     import gpu, os
#     from gpu_extras.batch import batch_for_shader

#     imageName = "ldts.png"
#     pathTexture = str(Path("~/Desktop/ldts.png").expanduser())
#     foundSceneImage = 0
#     loadedImage = None

#     for image in bpy.data.images:
#         if (image.name.find(imageName) != -1):
#             foundSceneImage += 1
#             loadedImage = image

#     if (foundSceneImage == 0):
#         loadedImage = bpy.data.images.load(pathTexture)

#     width = 1080
#     height = 1080
#     scale = 0.25

#     width = width*scale
#     height = height*scale

#     # For 2.93 specifically
#     tex = gpu.texture.from_image(loadedImage)

#     content = {
#         "pos": ((0, 0), (width, 0), (width, height), (0, height)),
#         "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
#     }

#     shader = gpu.shader.from_builtin("2D_IMAGE")
#     batch = batch_for_shader(shader, 'TRI_FAN', content)

#     def draw():
#         gpu.state.blend_set("ALPHA")
#         shader.bind()

#         shader.uniform_sampler("image", tex)
#         batch.draw(shader)

#     # For toggling on/off run script again
#     try:
#         bpy.context.space_data.draw_handler_remove(bpy.h, "WINDOW")
#         del bpy.h
#     except AttributeError:
#         bpy.h = bpy.context.space_data.draw_handler_add(draw, (), 'WINDOW', 'POST_PIXEL')
#     bpy.context.region.tag_redraw()


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
        #current_frame=scene.frame_current,
        tracks=tracks)
    
    if out == last_persisted:
        return out
    else:
        #print("NEW CHANGES")
        Path(jpath).write_text(json.dumps(out, indent=4))
        
        autosave = False
        for r in bpy.app.driver_namespace.get("_coldtypes", []):
            if hasattr(r, "reread_timeline"):
                r.reread_timeline()
            if hasattr(r, "autosave") and r.autosave:
                autosave = True
        
        if autosave:
            bpy.ops.wm.save_mainfile()
        return out
    

def render_as_image(r, res):
    from coldtype.pens.skiapen import SkiaPen

    path = r.filepath.parent / "renders" / (r.filepath.stem + "_livepreview.png")
    _ = SkiaPen.Precompose(res, r.rect, disk=str(path), scale=r.live_preview_scale)
    return path

    # if r.name not in bpy.data.images.keys():
    #     bpy.data.images.new(r.name, width=r.rect.w, height=r.rect.h, alpha=True, float_buffer=True)

    # img = bpy.data.images[r.name]
    # img.pixels = pimg.toarray(colorType=skia.ColorType.kRGBA_F32_ColorType).ravel()

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
            cfs = [r"^b3d_animation$", r"^b3d_sequencer$"]
        
        out = []

        # TODO unnecessary to do work of rendering b3d_sequencer results
        
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
                        if bpy.app.driver_namespace.get("_coldtype_live_preview", False):
                            lp_path = render_as_image(r, res)
                            if lp_path.name in bpy.data.images:
                                bpy.data.images[lp_path.name].reload()
                            else:
                                bpy.data.images.load(str(lp_path))
                    else:
                        raise Exception("r.renderer not supported", r.renderer)

            elif statics:
                if isinstance(r, b3d_runnable):
                    r.run()
                else:
                    walk_to_b3d(res, renderable=r)
                    if r.reset_to_zero:
                        bpy.data.scenes[0].frame_set(0)
        
        #if not animation_found:
        #    bpy.data.scenes[0].frame_set(0)

        if statics:
            bpy.app.driver_namespace["_coldtypes"] = out

        for o in out:
            if hasattr(o, "post_run") and o.post_run:
                o.post_run()
        
        return animation_found

    def reimport(self, arg):
        try:
            self.sr = SourceReader(arg, use_blender=True)
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
        ccf = bpy.app.driver_namespace.get("_coldtype_command_output_file")
        self.file = Path(ccf)

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
    input_file = command_file.replace(".txt", "_input.json")
    bpy.app.driver_namespace["_coldtype_command_output_file"] = command_file
    bpy.app.driver_namespace["_coldtype_command_input_file"] = input_file
    
    register_watcher()
    bpy.ops.wm.coldtype_watching_operator()
    add_internal_panel()
    add_external_panel()
    print("...waiting for coldtype...")