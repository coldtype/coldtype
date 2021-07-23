import bpy
from pathlib import Path
from runpy import run_path
import traceback

from coldtype.renderer.reader import SourceReader
from coldtype.blender import walk_to_b3d

#from coldtype.blender.watch import watch; watch()

# original idea: https://blender.stackexchange.com/questions/15670/send-instructions-to-blender-from-external-application

class ColdtypeWatchingOperator(bpy.types.Operator):
    bl_idname = "wm.coldtype_watching_operator"
    bl_label = "Coldtype Watching Operator"

    _timer = None
    file = Path("~/.coldtype/blender.txt").expanduser()
    state_file = Path("~/.coldtype/blender_state.txt").expanduser()
    sr = None
    current_frame = -1
    rendering = False

    def render_current_frame(self, statics=False):
        cfs = [r"^b3d_.*$"]
        if not statics:
            cfs.append(r".*animation$")
        
        for _, res in self.sr.frame_results(
            self.current_frame,
            class_filters=cfs):
            walk_to_b3d(res)
        
        if self.rendering:
            self.state_file.write_text(str(self.current_frame))
            print(">>>ANIMATIONRENDER", self.current_frame)
    
    def on_render_complete(self, canceled, scene):
        self.rendering = False
        if self.state_file.exists():
            self.state_file.unlink()
        if canceled:
            print(">RENDER CANCELED")
        else:
            print(">RENDER COMPLETED")
        bpy.data.scenes[0].frame_start = 0
    
    def start_full_render(self):
        if self.state_file.exists():
            last_frame = int(self.state_file.read_text())
            bpy.data.scenes[0].frame_start = last_frame

        self.rendering = True
        bpy.ops.render.render('INVOKE_DEFAULT',animation=True)

    def modal(self, context, event):
        if event.type == 'TIMER':
            if not self.file.exists():
                return {'PASS_THROUGH'}
            
            self.rendering = False
            
            for line in self.file.read_text().splitlines():
                line = line.rstrip("\n")
                cmd, arg = line.split(",")
                if cmd == 'import':
                    try:
                        self.sr = SourceReader(arg)
                        self.sr.unlink()
                        
                        bpy.data.scenes[0].frame_start = 0

                        def _frame_update_handler(scene):
                            #print("UPDATE", scene.frame_current, self.current_frame)

                            if scene.frame_current != self.current_frame:
                                self.current_frame = scene.frame_current
                                self.render_current_frame(statics=False)
                        
                        bpy.app.handlers.frame_change_post.clear()
                        bpy.app.handlers.frame_change_post.append(_frame_update_handler)
                        self.current_frame = bpy.context.scene.frame_current
                        self.render_current_frame(statics=True)
                    
                    except Exception as e:
                        self.current_frame = -1
                        bpy.app.handlers.frame_change_post.clear()
                        stack = traceback.format_exc()
                        print("---"*10)
                        print(stack)
                    
                    print(f"ran {arg}")

                    if self.state_file.exists():
                        self.start_full_render()
                elif cmd == 'render':
                    self.start_full_render()
                elif cmd == 'cancel':
                    self.cancel( context )
                else:
                    print('unknown request=%s arg=%s' % (cmd,arg))
            self.file.unlink()

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)

        def on_render_complete(scene):
            self.on_render_complete(False, scene)
        
        def on_render_canceled(scene):
            self.on_render_complete(True, scene)

        bpy.app.handlers.render_complete.append(on_render_complete)
        bpy.app.handlers.render_cancel.append(on_render_canceled)

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