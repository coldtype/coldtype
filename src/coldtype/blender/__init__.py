# to be loaded from within Blender

from enum import Enum
import os, math, json, time
from pathlib import Path
from coldtype.geometry import curve

from coldtype.geometry.rect import Rect
from coldtype.runon.path import P
from coldtype.pens.blenderpen import BlenderPen, BlenderPenCube, BPH
from coldtype.color import hsl

from coldtype.timing import Frame, Timeline, Timeable
from coldtype.renderable import renderable, Overlay, Action, runnable
from coldtype.renderable.animation import animation

from coldtype.blender.render import blend_source
from coldtype.timing.sequence import ClipTrack, Clip, Sequence

from coldtype.blender.fluent import BpyWorld, BpyObj, BpyCollection, BpyGroup, BpyMaterial

from typing import Callable

try:
    import bpy # noqa
except ImportError:
    bpy = None
    pass


class BlenderIO():
    def __init__(self, file):
        file = Path(str(file)).expanduser()
        #file.parent.mkdir(exist_ok=True, parents=True)

        self.blend_file = file
        self.data_file = Path(str(file) + ".json")
    
    def data(self):
        if self.data_file.exists():
            return json.loads(self.data_file.read_text())


class BlenderTimeline(Timeline):
    def __init__(self, file, duration=None, **kwargs):
        if isinstance(file, BlenderIO):
            file = file.data_file

        self.file = file
        if not self.file.exists():
            self.file.write_text("{}")
        
        data = json.loads(file.read_text())

        timeables = []
        for track in data.get("tracks", []):
            for tidx, t in enumerate(track["clips"]):
                timeables.append(Timeable(
                    t["start"],
                    t["end"],
                    name=t["text"],
                    index=tidx,
                    track=track["index"]))
        
        self.workarea = range(
            data.get("start", 0),
            data.get("end", 30)+1)
    
        super().__init__(
            fps=data.get("fps", 30)
            , timeables=timeables
            , start=0
            , end=duration or data.get("end")+1
            , **kwargs)

        # super().__init__(
        #     duration,
        #     fps,
        #     [data.get("current_frame", 0)],
        #     tracks,
        #     workarea_track=workarea_track-1)


def b3d(callback:Callable[[BlenderPen], BlenderPen],
    collection="Coldtype",
    primitive=None,
    dn=False,
    cyclic=True,
    material=None,
    zero=False,
    upright=False,
    tag_prefix=None,
    ):
    if not bpy: # short-circuit if this is meaningless
        return lambda x: x

    pen_mod = None
    if callback and not callable(callback):
        pen_mod = callback[0]
        callback = callback[1]

    def annotate(pen:P):
        if bpy and bpy.data and pen_mod:
            pen_mod(pen)
        
        prev = pen.data("b3d", {})
        if prev:
            callbacks = [*prev.get("callbacks"), callback]
        else:
            callbacks = [callback]

        #c = None
        #if zero:
        #    c = pen.ambit().pc
        #    pen.translate(-c.x, -c.y)

        pen.data(b3d=dict(
            collection=(collection
                or prev.get("collection", "Coldtype")),
            callbacks=callbacks,
            material=(material
                or prev.get("material", "ColdtypeDefault")),
            tag_prefix=(tag_prefix or prev.get("tag_prefix")),
            dn=dn,
            cyclic=cyclic,
            primitive=primitive,
            zero=zero,
            #reposition=c,
            upright=upright))
    
    return annotate


def b3d_post(callback:Callable[[BlenderPen], BlenderPen]):
    if not bpy: # short-circuit for non-bpy
        return lambda x: x

    def _b3d_post(pen:P):
        prev = pen.data("b3d_post")
        if prev:
            callbacks = [*prev, callback]
        else:
            callbacks = [callback]
        pen.data(b3d_post=callbacks)
    
    return _b3d_post


def b3d_pre(callback:Callable[[P], P]):
    def _cast(pen:P):
        if bpy and bpy.data:
            callback(pen)
    return _cast


def walk_to_b3d(result:P,
    dn=False,
    renderable=None,
    ):
    built = {}

    center = renderable.center
    center_rect = renderable.rect

    def walker(p:P, pos, data):
        bp = None

        if pos == 0:
            bdata = p.data("b3d")
            if not bdata:
                p.ch(b3d(lambda bp: bp.extrude(0.01)))
                bdata = p.data("b3d")
            
            zero = bdata.get("zero", False)

            if center and True:
                cx = -center_rect.w/2*(1-center[0])
                cy = -center_rect.h/2*(1-center[1])
                p.translate(cx, cy)

            pc = p.ambit().pc
            if zero:
                p.translate(-pc.x, -pc.y)
            
            if p.tag() is None:
                tag = data["utag"]
                if bdata.get("tag_prefix"):
                    tag = bdata.get("tag_prefix") + tag
                else:
                    tag = "ct_autotag_" + tag
                p.tag(tag)

            if bdata:
                coll = BPH.Collection(bdata["collection"])
                material = bdata.get("material", "ColdtypeDefault")

                if len(p.v.value) == 0:
                    p.hide()

                denovo = bdata.get("dn", dn)
                cyclic = bdata.get("cyclic", True)

                primitive = bdata.get("primitive")

                if primitive is not None:
                    _class = BlenderPen
                    if primitive == "cube":
                        _class = BlenderPenCube
                    
                    bp = p.cast(_class).draw(coll, primitive=primitive, material=material, dn=True)
                else:
                    bp = p.cast(BlenderPen).draw(coll, dn=denovo, material=material, cyclic=cyclic)
                
                bp.rotate(0)
                
                if bdata.get("callbacks"):
                    for cb in bdata.get("callbacks"):
                        cb(bp)

                bp.hide(not p._visible)

                # if center and False:
                #     cx = -center_rect.w/2*(1-center[0])
                #     cy = -center_rect.h/2*(1-center[1])
                #     bp.locate_relative(cx/100, cy/100)

                if renderable:
                    if renderable.upright:
                        bp.rotate(90)

                if zero: #bdata.get("reposition"):
                    pt = pc #bdata.get("reposition")
                    if bdata.get("upright"):
                        bp.locate_relative(pt.x/100, 0, pt.y/100)
                    else:
                        bp.locate_relative(pt.x/100, pt.y/100)
                
                built[p.tag()] = (p, bp)

        if pos == 0 or pos == 1:
            b3d_post = p.data("b3d_post")
            if b3d_post:
                for post in b3d_post:
                    post(bp)
                
    result.walk(walker)


class B3DPlayback(Enum):
    AlwaysStop = 0
    AlwaysPlay = 1
    KeepPlaying = 2


class b3d_runnable(runnable):
    def __init__(self,
        solo=False,
        cond=None,
        once=True,
        delay=False,
        playback:B3DPlayback=B3DPlayback.AlwaysStop,
        force_refresh=False,
        ):
        self.once = once
        self.delay = delay
        self.playback = playback
        self.force_refresh = force_refresh

        if cond is not None:
            super().__init__(solo=solo, cond=lambda: cond and bool(bpy) and bool(bpy.data))
        else:
            super().__init__(solo=solo, cond=lambda: bool(bpy) and bool(bpy.data))
    
    def run(self):
        if not bpy:
            return None
        else:
            return self.func(BpyWorld().deselect_all())


class b3d_renderable(renderable):
    def __init__(self,
        rect=(1080, 1080),
        center=(0, 0),
        upright=False,
        post_run=None,
        reset_to_zero=False,
        force_refresh=False,
        **kwargs
        ):
        self.center = center
        self.upright = upright
        self.post_run = post_run
        self.blender_io:BlenderIO = None
        self.reset_to_zero = reset_to_zero
        self.force_refresh = force_refresh

        super().__init__(rect, **kwargs)


class b3d_animation(animation):
    def __init__(self,
        rect=(1080, 1080),
        samples=-1,
        denoise=False,
        match_length=True,
        match_output=True,
        match_fps=True,
        bake=False,
        center=(0, 0),
        upright=False,
        autosave=False,
        renderer="b3d",
        force_refresh=False,
        **kwargs
        ):
        self.func = None
        self.name = None
        self.current_frame = -1
        
        self.samples = samples
        self.denoise = denoise
        self.bake = bake
        self.center = center
        self.upright = upright
        self.match_length = match_length
        self.match_output = match_output
        self.match_fps = match_fps
        self.renderer = renderer
        self.autosave = autosave
        self.force_refresh = force_refresh

        self._bt = False
        self.blender_io:BlenderIO = None

        if "timeline" not in kwargs:
            kwargs["timeline"] = Timeline(30)
        
        super().__init__(rect=rect, **kwargs)
        
        do_match_length = self.match_length

        if bpy and bpy.data and do_match_length:
            bpy.data.scenes[0].frame_start = 0
            bpy.data.scenes[0].frame_end = self.t.duration-1
        
        if bpy and bpy.data and self.match_fps:
            # don't think this is totally accurate but good enough for now
            if isinstance(self.t.fps, float):
                bpy.data.scenes[0].render.fps = round(self.t.fps)
                bpy.data.scenes[0].render.fps_base = 1.001
            else:
                bpy.data.scenes[0].render.fps = self.t.fps
                bpy.data.scenes[0].render.fps_base = 1
        
        if isinstance(self.timeline, BlenderTimeline):
            self.add_watchee(self.timeline.file)
    
    def post_read(self):
        out = super().post_read()
        if bpy and bpy.data and self.match_output:
            bpy.data.scenes[0].render.filepath = str(self.pass_path(index=None))
        return out
        
    def running_in_viewer(self):
        return not bpy or bpy.data
    
    def rasterize(self, config, content, rp):
        if self.renderer == "skia":
            return super().rasterize(config, content, rp)
        
        try:
            from b3denv import get_vars
            b3d_vars = get_vars(None)
            blender_path = Path(b3d_vars["blender"])
        except:
            raise Exception("NO BLENDER FOUND (via b3denv)")
        
        fi = rp.args[0].i
        blend_source(blender_path,
            self.filepath,
            self.blender_io.blend_file,
            fi,
            self.pass_path(index=None),
            self.samples,
            denoise=self.denoise)
        return True
    
    def baked_frames(self):
        def bakewalk(p, pos, data):
            if pos == 0:
                fi = data["idx"][0]
                (p.ch(b3d(callback=lambda bp: bp
                        .show_on_frame(fi)
                        .print(f"Baking frame {fi}..."),
                    collection=f"CTBakedAnimation_{self.name}",
                    dn=True,
                    tag_prefix=f"ct_baked_frame_{fi}_{self.name}__")))
        
        to_bake = P()
        for ps in self.passes(Action.RenderAll, None)[:]:
            to_bake += self.run_normal(ps, None)
        
        return to_bake.walk(bakewalk)


class b3d_sequencer(b3d_animation):
    def __init__(self,
        rect=Rect(1080, 1080),
        autosave=True,
        in_blender=False,
        match_output=False,
        live_preview=True,
        live_preview_scale=0.25,
        **kwargs
        ):
        self.live_preview = live_preview
        self.live_preview_scale = live_preview_scale

        super().__init__(
            rect=rect,
            match_fps=True,
            match_length=False,
            match_output=match_output,
            autosave=autosave,
            renderer="b3d" if in_blender else "skia",
            **kwargs)