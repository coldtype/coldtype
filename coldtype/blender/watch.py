import bpy, traceback, json, shutil
from pathlib import Path
from collections import defaultdict
from coldtype.renderable.animation import animation

from coldtype.renderer.reader import SourceReader
from coldtype.blender import B3DPlayback, b3d_animation, b3d_renderable, b3d_runnable, b3d_sequencer, walk_to_b3d
from coldtype.blender.timedtext import add_2d_panel
from coldtype.blender.panel3d import add_3d_panel
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

    if isinstance(res, Path) or isinstance(res, str) or False:
        prp = Path(str(res))
        if prp.exists():
            shutil.copy(str(prp), str(path))
    else:
        _ = SkiaPen.Precompose(res, r.rect, disk=str(path), scale=r.live_preview_scale)
    
    return path

    # if r.name not in bpy.data.images.keys():
    #     bpy.data.images.new(r.name, width=r.rect.w, height=r.rect.h, alpha=True, float_buffer=True)

    # img = bpy.data.images[r.name]
    # img.pixels = pimg.toarray(colorType=skia.ColorType.kRGBA_F32_ColorType).ravel()

# original idea: https://blender.stackexchange.com/questions/15670/send-instructions-to-blender-from-external-application

def display_image_in_blender(img_path):
    try:
        if img_path.name in bpy.data.images:
            bpy.data.images[img_path.name].reload()
        else:
            bpy.data.images.load(str(img_path))
    except RuntimeError:
        print("> failed to load livepreview")


class ColdtypeWatchingOperator(bpy.types.Operator):
    bl_idname = "wm.coldtype_watching_operator"
    bl_label = "Coldtype Watching Operator"

    _timer = None
    file = None
    sr = None
    current_frame = -1
    persisted = None

    _delayed_runnables = []
    _should_start_playing = False

    def render_current_frame(self, statics=False):
        delayed_runnables = []
        out = []
        animation_found = False
        frame = self.current_frame
        prerendered = bpy.app.driver_namespace.get("_coldtype_prerendered", False)
        playback = B3DPlayback.AlwaysStop

        def display_image(r, result):
            lp_path = render_as_image(r, result)
            display_image_in_blender(lp_path)
        
        candidates = self.candidates

        for r in candidates:
            if isinstance(r, b3d_runnable):
                if statics:
                    playback = r.playback
        
        if statics and playback != B3DPlayback.KeepPlaying:
            if bpy.context.screen.is_animation_playing:
                bpy.ops.screen.animation_play() # stop it

        for r in candidates:
            if isinstance(r, b3d_runnable):
                if r.once:
                    if statics:
                        if r.delay:
                            delayed_runnables.append(r)
                        else:
                            r.run()
                else:
                    if r.delay:
                        delayed_runnables.append(r)
                    else:
                        r.run()
            else:
                out.append(r)

                ps = r.passes(None, None, indices=[frame])
                def run_passes():
                    return r.run_normal(ps[0], renderer_state=None)
            
                if isinstance(r, b3d_sequencer) and r.renderer == "skia":
                    animation_found = True

                    if r.live_preview:
                        if prerendered:
                            result = ps[0].output_path
                        else:
                            result = run_passes()
                        display_image(r, result)
                
                elif isinstance(r, b3d_animation):
                    if r.bake:
                        if statics:
                            walk_to_b3d(r.baked_frames(), renderable=r)
                            if r.reset_to_zero:
                                bpy.data.scenes[0].frame_set(0)
                    else:
                        animation_found = True
                        result = run_passes()
                        if result:
                            if r.renderer == "b3d":
                                walk_to_b3d(result, renderable=r)
                            else:
                                raise Exception("r.renderer not supported", r.renderer)
                        
                        if r.reset_to_zero:
                            bpy.data.scenes[0].frame_set(0)
                        
                        if prerendered:
                            display_image(r, ps[0].output_path)
            
                elif isinstance(r, b3d_renderable):
                    # coolio
                    if statics:
                        result = run_passes()
                        walk_to_b3d(result, renderable=r)
                        if r.reset_to_zero:
                            bpy.data.scenes[0].frame_set(0)
        
        #if not animation_found:
        #    bpy.data.scenes[0].frame_set(0)

        if statics:
            bpy.app.driver_namespace["_coldtypes"] = out

        for o in out:
            if hasattr(o, "post_run") and o.post_run:
                o.post_run()
        
        if statics:
            self._delayed_runnables = delayed_runnables

            # for dr in self._delayed_runnables:
            #     dr.run()
            
            # self._delayed_runnables = []

            if playback == B3DPlayback.AlwaysPlay:
                bpy.ops.screen.animation_play()
        
        return animation_found

    def reimport(self, arg, inputs):
        try:
            self.sr = SourceReader(arg, use_blender=True, inputs=inputs)
            self.sr.unlink()
            self.candidates = self.sr.renderables()
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
            
            for dr in self._delayed_runnables:
                dr.run()
            
            self._delayed_runnables = []

            # if self._should_start_playing:
            #     if not bpy.context.screen.is_animation_playing:
            #         bpy.ops.screen.animation_play()
            #     self._should_start_playing = False

            if bpy.app.driver_namespace.get("_coldtype_needs_rerender", False):
                bpy.app.driver_namespace["_coldtype_needs_rerender"] = False
                self.render_current_frame(statics=False)

            if not bpy.context.screen.is_animation_playing:
                self.persisted = persist_sequence(self.persisted)

            if not self.file.exists():
                return {'PASS_THROUGH'}
            
            for line in self.file.read_text().splitlines():
                #print(line)
                try:
                    line = line.rstrip("\n")
                    start, kwargs = [t.strip() for t in line.split(";")]
                    kwargs = eval(kwargs)
                    cmd, arg = start.split(",")
                    if cmd == 'import':
                        self.reimport(arg, kwargs)
                    elif cmd == "play_preview":
                        bpy.ops.screen.animation_play()
                    elif cmd == "frame_offset":
                        bpy.ops.screen.frame_offset(delta=int(arg))
                    elif cmd == "refresh_sequencer":
                        bpy.ops.sequencer.refresh_all()
                        for k, v in bpy.data.images.items():
                            print("RELOAD", k, v)
                            v.reload()
                    elif cmd == "refresh_sequencer_and_image":
                        bpy.ops.sequencer.refresh_all()
                        for k, v in bpy.data.images.items():
                            if "_last_render.png" in k:
                                v.reload()
                    elif cmd == 'cancel':
                        self.cancel(context)
                    else:
                        print('unknown request=%s arg=%s' % (cmd,arg))
                except Exception as e:
                    print("Failed to read command file:", e)
            
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
    
    add_3d_panel()
    add_2d_panel()

    print("...blender waiting for coldtype...")