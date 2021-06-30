# to be loaded from within Blender

import os
from coldtype.pens.datpen import DATPen, DATPens
from coldtype.pens.blenderpen import BlenderPen, BPH

from coldtype.time import Frame
from coldtype.renderable import renderable
from coldtype.renderable.animation import animation

from coldtype.blender.render import blend_source

try:
    import bpy
except ImportError:
    bpy = None
    pass

def b3d(collection, callback=None, plane=False, dn=False):
    pen_mod = None
    if callback and not callable(callback):
        pen_mod = callback[0]
        callback = callback[1]

    def _cast(pen:DATPen):
        if bpy and pen_mod:
            pen_mod(pen)
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
    def __init__(self, rect=(1080, 1080), **kwargs): # TODO possible to read from project? or alternatively to set this duration on the project? feel like that'd be more coldtype-y
        self.func = None
        self.name = None
        self.current_frame = -1
        super().__init__(rect=rect, **kwargs)

        if bpy:
            bpy.data.scenes[0].frame_end = self.t.duration-1
    
    def update(self):        
        result:DATPens = self.func(Frame(self.current_frame, self))
        _walk_to_b3d(result)
    
    def __call__(self, func):
        if not bpy or bpy.app.background:
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
                blend_source(
                    __FILE__,
                    blend_file,
                    a.i,
                    output_dir,
                    samples=samples)
        os.system("afplay /System/Library/Sounds/Pop.aiff")
    
    def blender_render_frame(self, blend_file, fi, samples=4):
        blend_source(__FILE__, blend_file, fi, self.blender_output_dir(), samples)


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
    from coldtype.text.composer import StSt, Font
    from coldtype.color import hsl

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
    
    @b3d_animation(timeline=60, bg=0, layer=0, rstate=1)
    def draw_dps(f, rs):
        if not bpy and not rs.previewing:
            draw_dps.blender_render_frame("scratch.blend", f.i)

        txt = (StSt("CHROMATIC", fnt4, 330, palette=4)
            .align(f.a.r)
            .collapse()
            .map(lambda i, p: p.explode())
            .collapse()
            .pmap(lambda i,p: p
                .declare(fa:=f.adj(-i*1))
                .cond(p.ambit().y > 570, lambda pp:
                    pp.translate(0, fa.e("seio", 2, rng=(50, 0))))
                .cond(p.ambit().mxy < 490, lambda pp:
                    pp.translate(0, fa.e("seio", 2, rng=(-50, 0))))
                .tag(f"Hello{i}")
                .chain(b3d("Text", lambda bp: bp
                    .extrude(fa.e("eeio", 1, rng=(0.25, 5)))
                    .metallic(1)))))
        
        return DATPens([
            (DATPen(f.a.r.inset(-500))
                .f(hsl(0.5, 0.7, 0.3))
                .f(0)
                .tag("BG")
                .ch(b3d("Text", plane=1))),
            txt])
    
    if not bpy:
        from coldtype.img.skiaimage import SkiaImage
    
    @animation(draw_dps.rect, timeline=draw_dps.timeline, preview_only=1)
    def draw_dps_blender_version(f):
        try:
            return SkiaImage(draw_dps.blender_output_dir() / "{:04d}.png".format(f.i))
        except:
            pass
    
    def build(artifacts):
        draw_dps.blender_render("scratch.blend", artifacts[:1], samples=8)

    def release(artifacts):
        draw_dps.blender_render("scratch.blend", artifacts, samples=8)