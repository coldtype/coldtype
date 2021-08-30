import bpy
from pathlib import Path
from runpy import run_path
import traceback

from coldtype.renderer.reader import SourceReader
from coldtype.blender import b3d_animation, walk_to_b3d

#from coldtype.blender.watch import watch; watch()

# original idea: https://blender.stackexchange.com/questions/15670/send-instructions-to-blender-from-external-application

class ColdtypeWatchingOperator(bpy.types.Operator):
    bl_idname = "wm.coldtype_watching_operator"
    bl_label = "Coldtype Watching Operator"

    _timer = None
    file = Path("~/.coldtype/blender.txt").expanduser()
    sr = None
    current_frame = -1

    def render_current_frame(self, statics=False):
        animation_found = False

        cfs = [r"^b3d_.*$"]
        if not statics:
            cfs = [r"^b3d_animation$"]
        
        for r, res in self.sr.frame_results(
            self.current_frame,
            class_filters=cfs
            ):

            if isinstance(r, b3d_animation):
                if r.bake:
                    if statics:
                        walk_to_b3d(r.baked_frames(), renderable=r)
                else:
                    animation_found = True
                    walk_to_b3d(res, renderable=r)
            elif statics:
                walk_to_b3d(res, renderable=r)
        
        if not animation_found:
            bpy.data.scenes[0].frame_set(0)
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
                elif cmd == 'cancel':
                    self.cancel( context )
                else:
                    print('unknown request=%s arg=%s' % (cmd,arg))
            
            if self.file.exists():
                self.file.unlink()

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
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

def watch():
    register_watcher()
    bpy.ops.wm.coldtype_watching_operator()
    print("...waiting for coldtype...")