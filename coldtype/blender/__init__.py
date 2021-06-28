# to be loaded from within Blender

import os
from coldtype.geometry import Point, Line, Rect
from coldtype.pens.datpen import DATPen, DATPens
from coldtype.pens.blenderpen import BlenderPen, BPH
from coldtype.text.reader import StyledString, Style, Font
from coldtype.text.composer import StSt
from coldtype.color import hsl, bw
from pathlib import Path

from coldtype.time import Frame
from coldtype.renderable import renderable
from coldtype.renderable.animation import animation

from coldtype.blender.render import blend_pickle

try:
    import bpy
except ImportError:
    bpy = None
    pass


def b3d(collection, callback=None, plane=False, dn=False):
    def _cast(pen:DATPen):
        pen.add_data("b3d", dict(
            collection=collection,
            callback=callback))
    return _cast


def _walk_to_b3d(result:DATPens, dn=False):
    def walker(p:DATPen, pos, data):
        if pos == 0:
            bdata = p.data.get("b3d")
            if bdata:
                coll = BPH.Collection(bdata["collection"])

                if bdata.get("plane"):
                    bp = p.cast(BlenderPen).draw(coll, plane=True)
                else:
                    bp = p.cast(BlenderPen).draw(coll, dn=dn)
                
                if bdata.get("callback"):
                    bdata.get("callback")(bp)
                    # if bdata.get("extrude"):
                    #     bp.extrude(bdata.get("extrude"))
                    # if bdata.get("rotate"):
                    #     bp.rotate(*bdata.get("rotate"))
                    # if bdata.get("metallic"):
                    #     bp.metallic(bdata.get("metallic"))
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
        super().__init__(**kwargs, fmt="pickle")
    
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
    
    def blender_output_dir(self):
        output_dir = self.output_folder / "_blender"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def blender_render(self, blend_file, artifacts, samples=4):
        output_dir = self.blender_output_dir()
        for a in artifacts[:]:
            if a.render == self:
                blend_pickle(blend_file, a.output_path, output_dir, samples=samples)
        os.system("afplay /System/Library/Sounds/Pop.aiff")


class b3d_animation_render(animation):
    def __init__(self, b3danim:b3d_animation):
        self.b3danim = b3danim
        super().__init__(rect=b3danim.rect, timeline=b3danim.timeline)
    
    def passes(self, action, renderer_state, indices=[]):
        passes = super().passes(action, renderer_state, indices)
        for p in passes:
            f = p.args[0]
            outf = self.b3danim.output_folder
            pickle = outf / "{:s}_{:04d}.pickle".format(outf.stem, f.i)
            p.args.append(pickle)
        return passes


if __name__ == "<run_path>":
    from coldtype.text.composer import Glyphwise

    fnt = Font.Cacheable("~/Type/fonts/fonts/CheeeVariable.ttf")
    fnt2 = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")
    fnt3 = Font.Cacheable("~/Type/fonts/fonts/SwearCilatiVariable.ttf")
    fnt4 = Font.Cacheable("~/Type/fonts/fonts/PappardelleParty-VF.ttf")
    fnt5 = Font.Cacheable("~/Type/fonts/fonts/JobClarendonVariable-VF.ttf")

    if bpy:
        bpy.app.handlers.frame_change_post.clear()

    #@b3d_renderable()
    def draw_bg(r):
        return DATPens([
            (DATPen(r.inset(0, 0)).f(hsl(0.07, 1, 0.3))
                .tag("BG2")
                .chain(b3d("Text", plane=1)))])
    
    @b3d_animation(timeline=60, bg=0, layer=0)
    def draw_dps(f):
        txt = (StSt("BLENDER", fnt4, 330, palette=4)
            .align(f.a.r)
            .collapse()
            .map(lambda i, p: p.explode())
            .collapse()
            .pmap(lambda i,p: p
                .declare(fa:=f.adj(-i*1))
                .cond(p.ambit().y > 570, lambda pp:
                    pp.translate(0, fa.e("eeio", 1, rng=(50, 0))))
                .cond(p.ambit().mxy < 490, lambda pp:
                    pp.translate(0, fa.e("eeio", 1, rng=(-50, 0))))
                .tag(f"Hello{i}")
                .chain(b3d("Text", lambda bp: bp
                    .extrude(fa.e("eeio", 1, rng=(0.25, 7)))
                    .metallic(0.1)))))
        
        return DATPens([
            (DATPen(f.a.r.inset(-500))
                .f(hsl(0.9))
                .tag("BG")
                .ch(b3d("Text", plane=1))),
            #txt2.rotate(45).translate(-100, -10),
            txt
            ])
    
    if not bpy:
        from coldtype.img.skiaimage import SkiaImage
    
    @animation(draw_dps.rect, timeline=draw_dps.timeline, preview_only=1)
    def draw_dps_blender_version(f):
        try:
            return SkiaImage(draw_dps.blender_output_dir() / "{:04d}.png".format(f.i))
        except:
            pass
    
    def build(artifacts):
        draw_dps.blender_render("scratch.blend", artifacts[:2], samples=2)

    def release(artifacts):
        draw_dps.blender_render("scratch.blend", artifacts, samples=2)

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