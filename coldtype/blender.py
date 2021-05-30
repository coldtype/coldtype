# to be loaded from within Blender

from drafting.geometry import Point, Line, Rect
from drafting.pens.drawbotpen import DrawBotPen
from drafting.pens.draftingpen import DraftingPen
from drafting.pens.draftingpens import DraftingPens
from drafting.pens.blenderpen import BlenderPen, BPH
from drafting.text.reader import StyledString, Style, Font
from drafting.text.composer import StSt
from drafting.color import hsl, bw
from pathlib import Path
try:
    import bpy
except ImportError:
    print("no bpy")
    pass

from drafting.time.timeline import Timeline
from drafting.time.timeable import Timeable
from drafting.time import Frame

class b3d_animation(Timeable):
    def __init__(self, duration=10): # TODO possible to read from project?
        self.func = None
        self.name = None
        self.current_frame = -1
        self.start = 0
        self.end = duration
        self.timeline = Timeline(duration)
        self.t = self.timeline
    
    def update(self):
        self.func(Frame(self.current_frame, self))
    
    def __call__(self, func):
        self.func = func
        if not self.name:
            self.name = self.func.__name__

        def _frame_update_handler(scene):
            if scene.frame_current != self.current_frame:
                self.current_frame = scene.frame_current
                self.update()
        
        bpy.app.handlers.frame_change_post.clear() # TODO look for closure one only?
        bpy.app.handlers.frame_change_post.append(_frame_update_handler)

        self.current_frame = bpy.context.scene.frame_current
        self.update()
        return self