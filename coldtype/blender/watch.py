import bpy
from pathlib import Path
from runpy import run_path
import traceback

from coldtype.renderer.reader import SourceReader

#from coldtype.blender.watch import watch; watch()

# original idea: https://blender.stackexchange.com/questions/15670/send-instructions-to-blender-from-external-application

class ColdtypeWatchingOperator(bpy.types.Operator):
    bl_idname = "wm.coldtype_watching_operator"
    bl_label = "Coldtype Watching Operator"

    _timer = None
    file = Path("~/.coldtype-blender.txt").expanduser()

    def modal(self, context, event):
        if event.type == 'TIMER':
            if not self.file.exists():
                return {'PASS_THROUGH'}
            
            for line in self.file.read_text().splitlines():
                line = line.rstrip("\n")
                cmd,arg = line.split(",")
                if cmd == 'import':
                    try:
                        sr = SourceReader(arg)
                        sr.unlink()
                    except Exception as e:
                        stack = traceback.format_exc()
                        print("---"*10)
                        print(stack)
                    print(f"ran {arg}")
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