# to be loaded from within Blender

from coldtype.geometry import Point, Line, Rect
from coldtype.pens.drawbotpen import DrawBotPen
from coldtype.pens.datpen import DATPen, DATPens
from coldtype.pens.blenderpen import BlenderPen, BPH
from coldtype.text.reader import StyledString, Style, Font
from coldtype.text.composer import StSt
from coldtype.color import hsl, bw
from runpy import run_path
from pathlib import Path

from coldtype.renderable.animation import animation


try:
    import bpy
except ImportError:
    bpy = None
    pass

from coldtype.time import Frame


def b3d(collection,
    extrude=None,
    rotate=None,
    ):
    def _annotate(pen:DATPen):
        pen.add_data("b3d", dict(
            collection=collection,
            extrude=extrude,
            rotate=rotate))
    return _annotate


class b3d_animation(animation):
    def __init__(self, **kwargs): # TODO possible to read from project? or alternatively to set this duration on the project? feel like that'd be more coldtype-y
        self.func = None
        self.name = None
        self.current_frame = -1
        super().__init__(**kwargs)
    
    def update(self):
        def walker(p:DATPen, pos, data):
            if pos == 0:
                bdata = p.data.get("b3d")
                print(p)
                if bdata:
                    bp = p.cast(BlenderPen).draw(BPH.Collection(bdata["collection"]))
                    if bdata.get("extrude"):
                        bp.extrude(bdata.get("extrude"))
                    if bdata.get("rotate"):
                        bp.rotate(*bdata.get("rotate"))
        
        result:DATPens = self.func(Frame(self.current_frame, self))
        result.walk(walker)
    
    def __call__(self, func):
        if not bpy:
            return super().__call__(func)

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

r = Rect(0, 0, 1000, 1000)
fnt = Font.Cacheable("~/Type/fonts/fonts/CheeeVariable.ttf")

if bpy:
    BPH.Clear() # does this not even work?

@b3d_animation(rect=r, timeline=30)
def draw_txt(f):
    return DATPens([
        (StSt("COLDTYPE IN", fnt, 100, yest=0, grvt=0)
            .pen()
            .align(r.take(0.5, "mxy"))
            .f(hsl(0.8, 1))
            .tag("CLD")
            .chain(b3d("Text",
                extrude=f.e(1, rng=(0.05, 2))))),
        (StSt("3D", fnt, 500,
            yest=f.ie("eeio", 2),
            grvt=f.e(1))
            .pen()
            .align(r.take(0.85, "mny"))
            .tag("3D")
            .chain(b3d("Text",
                extrude=f.e(1, rng=(0.05, 3)),
                rotate=(f.e(1, rng=(0, 15)), None, None))))])