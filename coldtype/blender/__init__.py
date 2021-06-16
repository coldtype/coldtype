# to be loaded from within Blender

from coldtype.geometry import Point, Line, Rect
from coldtype.pens.datpen import DATPen, DATPens
from coldtype.pens.blenderpen import BlenderPen, BPH
from coldtype.text.reader import StyledString, Style, Font
from coldtype.text.composer import StSt
from coldtype.color import hsl, bw
from pathlib import Path

from coldtype.renderable import renderable
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
    plane=False,
    ):
    def _annotate(pen:DATPen):
        pen.add_data("b3d", dict(
            collection=collection,
            extrude=extrude,
            rotate=rotate,
            plane=plane))
    return _annotate


def _walk_to_b3d(result:DATPens):
    def walker(p:DATPen, pos, data):
        if pos == 0:
            bdata = p.data.get("b3d")
            if bdata:
                coll = BPH.Collection(bdata["collection"])

                if bdata.get("plane"):
                    bp = p.cast(BlenderPen).draw(coll, plane=True)
                else:
                    bp = p.cast(BlenderPen).draw(coll)
                    if bdata.get("extrude"):
                        bp.extrude(bdata.get("extrude"))
                    if bdata.get("rotate"):
                        bp.rotate(*bdata.get("rotate"))
    result.walk(walker)


class b3d_renderable(renderable):
    def update(self):
        _walk_to_b3d(self.func(self.rect))

    def __call__(self, func):
        if not bpy:
            return super().__call__(func)

        self.func = func
        if not self.name:
            self.name = self.func.__name__
        
        self.update()
        return self


class b3d_animation(animation):
    def __init__(self, hidden=False, **kwargs): # TODO possible to read from project? or alternatively to set this duration on the project? feel like that'd be more coldtype-y
        self.func = None
        self.name = None
        self.current_frame = -1
        self.hidden = hidden
        super().__init__(**kwargs)
    
    def update(self):        
        result:DATPens = self.func(Frame(self.current_frame, self))
        _walk_to_b3d(result)
    
    def __call__(self, func):
        if not bpy:
            return super().__call__(func)

        self.func = func
        if not self.name:
            self.name = self.func.__name__

        def _frame_update_handler(scene):
            #print("UPDATE", self.name)
            if scene.frame_current != self.current_frame:
                self.current_frame = scene.frame_current
                self.update()
        
        bpy.app.handlers.frame_change_post.clear() # TODO look for closure one only?
        bpy.app.handlers.frame_change_post.append(_frame_update_handler)

        self.current_frame = bpy.context.scene.frame_current
        self.update()
        return self


if __name__ == "<run_path>":
    from coldtype.text.composer import Glyphwise

    fnt = Font.Cacheable("~/Type/fonts/fonts/CheeeVariable.ttf")
    fnt2 = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

    if bpy:
        bpy.app.handlers.frame_change_post.clear()

    @b3d_renderable()
    def draw_bg(r):
        return DATPens([
            (DATPen(r.inset(0, 0)).f(hsl(0.07, 1, 0.3))
                .tag("BG2")
                .chain(b3d("Text", plane=1)))])
    
    @b3d_animation(timeline=120, layer=1)
    def draw_dps(f):
        return (Glyphwise("Wavey", lambda i,c: Style(fnt2, 300, wdth=f.adj(-i*5).e("seio", 1, rng=(0, 0.75)), slnt=1))
            .align(f.a.r)
            .pmap(lambda i,p: p
                .tag(f"Hello{i}")
                .chain(b3d("Text", extrude=f.adj(-i*5).e("seio", 1, rng=(0, 5))))))

    #@b3d_animation(timeline=30, layer=1)
    def draw_txt(f):
        return DATPens([
            (StSt("THREEE", fnt2, 100, tu=f.e(1, rng=(0, 1000)),
                wdth=f.e(1, rng=(0.25, 1)), wght=1, slnt=f.e(1),
                rotate=f.e(1, rng=(0, 360)))
                .pen()
                .align(f.a.r.take(0.5, "mxy"))
                .f(hsl(0.7, 1))
                .tag("CLD")
                .chain(b3d("Text",
                    extrude=f.e(1, rng=(0.05, 2))))),
            (StSt("DEEE", fnt, 500 - f.ie("eeio", 2)*200,
                yest=f.ie("eeio", 2),
                grvt=f.e(1))
                .pen()
                .align(f.a.r.take(0.85, "mny"))
                .tag("3D")
                .chain(b3d("Text",
                    extrude=f.e(1, rng=(0.05, 7)),
                    rotate=(f.e(1, rng=(0, 15)), None, None))))])