# to be loaded from within Blender

import os, math
from pathlib import Path

from coldtype.geometry.rect import Rect
from coldtype.pens.datpen import DATPen, DATPens
from coldtype.pens.blenderpen import BlenderPen, BPH
from coldtype.color import hsl

from coldtype.time import Frame, Timeline
from coldtype.renderable import renderable, Overlay
from coldtype.renderable.animation import animation

from coldtype.blender.render import blend_source

try:
    import bpy # noqa
except ImportError:
    bpy = None
    pass

def b3d(collection,
    callback=None,
    plane=False,
    dn=False,
    material="auto",
    zero=False,
    upright=False,
    ):
    if not isinstance(collection, str):
        callback = collection
        collection = "Coldtype"

    pen_mod = None
    if callback and not callable(callback):
        pen_mod = callback[0]
        callback = callback[1]

    def _cast(pen:DATPen):
        if bpy and pen_mod:
            pen_mod(pen)

        c = pen.ambit().pc
        if zero:
            pen.translate(-c.x, -c.y)

        pen.add_data("b3d", dict(
            collection=collection,
            callback=callback,
            material=material,
            dn=dn,
            plane=plane,
            reposition=c,
            upright=upright))
    return _cast


def b3d_mod(callback):
    def _cast(pen:DATPen):
        if bpy:
            callback(pen)
    return _cast


class b3d_mods():
    @staticmethod
    def center(r:Rect):
        return b3d_mod(lambda p:
            p.translate(-r.w/2, -r.h/2))
    
    def centerx(r:Rect):
        return b3d_mod(lambda p:
            p.translate(-r.w/2, 0))
    
    def centery(r:Rect):
        return b3d_mod(lambda p:
            p.translate(0, -r.h/2))


def walk_to_b3d(result:DATPens, dn=False):
    def walker(p:DATPen, pos, data):
        if pos == 0:
            bdata = p.data.get("b3d")
            if not bdata:
                p.ch(b3d(lambda bp: bp.extrude(0.01)))
                bdata = p.data.get("b3d")
            
            if p.tag() == "?" and data.get("idx"):
               p.tag("ct_autotag_" + "_".join([str(i) for i in data["idx"]]))

            if bdata:
                coll = BPH.Collection(bdata["collection"])
                material = bdata.get("material", "auto")

                if len(p.value) == 0:
                    p.v(0)
                
                denovo = bdata.get("dn", dn)

                if bdata.get("plane"):
                    bp = p.cast(BlenderPen).draw(coll, plane=True, material=material, dn=True)
                else:
                    bp = p.cast(BlenderPen).draw(coll, dn=denovo, material=material)
                
                if bdata.get("callback"):
                    bdata.get("callback")(bp)

                bp.hide(not p._visible)

                if bdata.get("reposition"):
                    p = bdata.get("reposition")
                    if bdata.get("upright"):
                        bp.locate(p.x/100, 0, p.y/100)
                    else:
                        bp.locate(p.x/100, p.y/100)
                
    result.walk(walker)


class b3d_renderable(renderable):
    def post_read(self):
        if not hasattr(self, "blend"):
            self.blend = self.filepath.parent / "blends" / (self.filepath.stem + ".blend")

        if self.blend:
            self.blend = Path(self.blend).expanduser()
            self.blend.parent.mkdir(exist_ok=True, parents=True)

        super().post_read()
        # if bpy:
        #     bpy.data.scenes[0].render.filepath = str(self.pass_path(""))


class b3d_animation(animation):
    def __init__(self,
        rect=(1080, 1080),
        samples=16,
        denoise=True,
        blend=None,
        **kwargs
        ):
        self.func = None
        self.name = None
        self.current_frame = -1
        self.samples = samples
        self.denoise = denoise
        self.blend = blend
        
        if "timeline" not in kwargs:
            kwargs["timeline"] = Timeline(30)
        
        super().__init__(rect=rect, **kwargs)

        if bpy:
            bpy.data.scenes[0].frame_end = self.t.duration-1
            # don't think this is totally accurate but good enough for now
            if isinstance(self.t.fps, float):
                bpy.data.scenes[0].render.fps = round(self.t.fps)
                bpy.data.scenes[0].render.fps_base = 1.001
            else:
                bpy.data.scenes[0].render.fps = self.t.fps
                bpy.data.scenes[0].render.fps_base = 1
    
    def run(self, render_pass, renderer_state):
        fi = render_pass.args[0].i
        if renderer_state and not bpy:
            if renderer_state.previewing:
                if Overlay.Rendered in renderer_state.overlays:
                    from coldtype.img.skiaimage import SkiaImage
                    return SkiaImage(self.pass_path(fi))
        
        return super().run(render_pass, renderer_state)
    
    def rasterize(self, _, rp):
        fi = rp.args[0].i
        blend_source(self.filepath, self.blend, fi, self.pass_path(""), self.samples, denoise=self.denoise)
        return True
    
    def post_read(self):
        if not self.blend:
            self.blend = self.filepath.parent / "blends" / (self.filepath.stem + ".blend")

        if self.blend:
            self.blend = Path(self.blend).expanduser()
            self.blend.parent.mkdir(exist_ok=True, parents=True)

        super().post_read()
        if bpy:
            bpy.data.scenes[0].render.filepath = str(self.pass_path(""))
    
    def blender_rendered_preview(self, solo=0):
        if bpy: return
        
        from coldtype.img.skiaimage import SkiaImage
        
        @animation(self.rect, timeline=self.timeline, preview_only=1, sort=1000, solo=solo)
        def blender_preview(f):
            try:
                return SkiaImage(self.pass_path(f.i))
            except:
                pass
        
        return blender_preview


# if __name__ == "<run_path>":
#     from coldtype.text.composer import StSt, Font
#     from coldtype.color import hsl

#     fnt = Font.Cacheable("~/Type/fonts/fonts/PappardelleParty-VF.ttf")

#     @b3d_renderable()
#     def draw_bg(r):
#         return DATPens([
#             (DATPen(r.inset(0, 0)).f(hsl(0.85, 1, 0.7))
#                 .tag("BG2")
#                 .chain(b3d("Text", plane=1)))])
    
#     @b3d_animation(timeline=Timeline(60, 30), bg=0, layer=1, rstate=1)
#     def draw_dps(f, rs):
#         if bpy:
#             bpy.data.objects['Light'].rotation_euler[2] = f.e("l", rng=(0, math.radians(360)), to1=0)
            
#             centroid = BPH.AddOrFind("Centroid",
#                 lambda: bpy.ops.object.empty_add(type="PLAIN_AXES"))
#             centroid.location = (5.4, 5.4, 0)
#             centroid.rotation_euler[2] = f.e("l", rng=(0, math.radians(360)), to1=0)

#         txt = (StSt("ABCDEFG", fnt, 330, palette=0)
#             .align(f.a.r)
#             .collapse()
#             .map(lambda i, p: p.explode())
#             .collapse()
#             .pmap(lambda i,p: p
#                 .declare(fa:=f.adj(-i*1))
#                 .cond(p.ambit().y > 570, lambda pp:
#                     pp.translate(0, fa.e("seio", 2, rng=(50, 0))))
#                 .cond(p.ambit().mxy < 490, lambda pp:
#                     pp.translate(0, fa.e("seio", 2, rng=(-50, 0))))
#                 .tag(f"Hello{i}")
#                 .chain(b3d_mods.center(f.a.r))
#                 .chain(b3d("Text", lambda bp: bp
#                     .extrude(fa.e("eeio", 1, rng=(0.25, 2)))
#                     .metallic(1)))))
        
#         return DATPens([txt])
    
#     previewer = draw_dps.blender_rendered_preview()
    
#     #def build(artifacts):
#     #    draw_dps.blender_render("scratch.blend", artifacts[:1], samples=8)

#     #def release(artifacts):
#     #    draw_dps.blender_render("scratch.blend", artifacts, samples=8)