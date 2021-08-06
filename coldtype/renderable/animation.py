import math, os, re
from typing import Tuple

from enum import Enum
from subprocess import run
from pathlib import Path
from datetime import datetime

from coldtype.helpers import loopidx, interp_dict
from coldtype.time.timeable import Timing, Timeable, TimeableSet
from coldtype.time import Frame
from coldtype.time.timeline import Timeline
from coldtype.time.loop import Loop, LoopPhase

from coldtype.text.reader import normalize_font_prefix, Font, Style
from coldtype.pens.datpen import DATPen, DATPens
from coldtype.pens.dattext import DATText
from coldtype.geometry import Rect, Point
from coldtype.color import normalize_color, hsl, bw

from coldtype.renderable.renderable import renderable, Action, RenderPass, Overlay


try:
    import skia
except ImportError:
    skia = None

try:
    import drawBot as db
    import AppKit
except ImportError:
    db = None


class animation(renderable, Timeable):
    """
    Base class for any frame-wise animation animatable by Coldtype
    """
    def __init__(self,
        rect=(1080, 1080),
        duration=10, # deprecated? redundant to timeline=10
        storyboard=[0],
        timeline:Timeline=None,
        show_frame=True,
        overlay=True,
        watch_render=None,
        write_start=0,
        **kwargs
        ):
        if watch_render:
            ws = kwargs.get("watch_soft", [])
            ws.append(watch_render)
            kwargs["watch_soft"] = ws
            self.watch_render = Path(watch_render).expanduser().absolute()
        else:
            self.watch_render = None

        super().__init__(**kwargs)
        self.rect = Rect(rect).round()
        self.r = self.rect
        self.overlay = overlay
        self.start = 0
        self.end = duration
        self.show_frame = show_frame
        self.write_start = write_start
        self.storyboard = storyboard
        if self.write_start and self.storyboard == [0]:
            self.storyboard = [self.write_start]

        if timeline:
            if not isinstance(timeline, Timeline):
                try:
                    timeline = Timeline(timeline[0], fps=timeline[1])
                except:
                    timeline = Timeline(timeline)
            self.timeline = timeline
            self.t = timeline
            self.start = timeline.start
            self.end = timeline.end
            
            if self.storyboard != [0] and timeline.storyboard == [0]:
                pass
            else:
                self.storyboard = timeline.storyboard.copy()
        else:
            self.timeline = Timeline(duration)
    
    def __call__(self, func):
        res = super().__call__(func)
        self.prefix = self.name + "_"
        return res
    
    def folder(self, filepath):
        return filepath.stem + "/" + self.name # TODO necessary?
    
    def all_frames(self):
        return list(range(0, self.duration))
    
    def _active_frames(self, renderer_state):
        if self.watch_render:
            for k, v in renderer_state.watch_soft_mods.items():
                if k.parent == self.watch_render.absolute():
                    fi = int(k.stem.split("_")[-1])
                    renderer_state.adjust_keyed_frame_offsets(self.name, lambda x, y: fi)

        frames = []
        if renderer_state:
            for f in renderer_state.get_frame_offsets(self.name):
                frames.append(f % self.duration)
        return frames
    
    def active_frames(self, action, renderer_state, indices):
        if not action:
            return indices
        
        frames = self._active_frames(renderer_state)

        if action == Action.RenderAll:
            frames = self.all_frames()
        elif action in [Action.PreviewIndices, Action.RenderIndices]:
            frames = indices
        elif action in [Action.RenderWorkarea]:
            if self.timeline:
                try:
                    frames = self.workarea()
                except:
                    frames = self.all_frames()
                #if hasattr(self.timeline, "find_workarea"):
                #    frames = self.timeline.find_workarea()
        #else:
        #    frames = indices
        return frames
    
    def workarea(self):
        return list(self.timeline.workareas[0])
    
    def jump(self, current, direction):
        c = current % self.duration
        js = self.timeline.jumps()
        if direction < 0:
            for j in reversed(js):
                if c > j:
                    return j
        else:
            for j in js:
                if c < j:
                    return j
        return current
    
    def pass_suffix(self, index):
        idx_offset = (index - self.write_start) % self.duration
        if self.suffix:
            return "{:s}_{:04d}".format(self.suffix, idx_offset)
        else:
            return "{:04d}".format(idx_offset)
    
    def passes(self, action, renderer_state, indices=[]):
        frames = self.active_frames(action, renderer_state, indices)
        return [RenderPass(self, action, self.pass_suffix(i), [Frame(i, self)]) for i in frames]
    
    def runpost(self, result, render_pass, renderer_state):
        #if Overlay.Rendered in renderer_state.overlays:
        #    from coldtype.img.skiaimage import SkiaImage
        #    return SkiaImage(render_pass.output_path)

        res = super().runpost(result, render_pass, renderer_state)
        if Overlay.Info in renderer_state.overlays and self.overlay:
            t = self.rect.take(50, "mny")
            frame:Frame = render_pass.args[0]
            return DATPens([
                res,
                DATPen().rect(t).f(bw(0, 0.75)) if self.show_frame else None,
                DATText(f"{frame.i} / {self.duration}", Style("Times", 42, load_font=0, fill=bw(1)), t.inset(10)) if self.show_frame else None])
        return res
    
    def package(self):
        pass

    def fn_to_frame(self, fn_name):
        return 0
    
    def frame_to_fn(self, fi) -> Tuple[str, dict]:
        return None, {}

    def contactsheet(self, gx, sl=slice(0, None, None)):
        try:
            sliced = True
            start, stop, step = sl.indices(self.duration)
            duration = (stop - start) // step
        except AttributeError: # indices storyboard
            duration = len(sl)
            sliced = False
        
        ar = self.rect
        gy = math.ceil(duration / gx)
        
        @renderable(rect=(ar.w*gx, ar.h*gy), bg=self.bg, name=self.name + "_contactsheet")
        def contactsheet(r:Rect):
            _pngs = list(sorted(self.output_folder.glob("*.png")))
            if sliced:
                pngs = _pngs[sl]
            else:
                pngs = [p for i, p in enumerate(_pngs) if i in sl]
            
            dps = DATPens()
            dps += DATPen().rect(r).f(self.bg)
            for idx, g in enumerate(r.grid(gx, gy)):
                if idx < len(pngs):
                    dps += DATPen().rect(g).f(None).img(pngs[idx], g, pattern=False)
            return dps
        
        return contactsheet
    
    def export(self, fmt, date=False, loops=1, open=1):
        def _export(passes):
            fe = FFMPEGExport(self, passes,
                date=date, loops=loops)
            if fmt == "gif":
                fe.gif()
            elif fmt == "h264":
                fe.h264()
            fe.write()
            if open:
                fe.open()
            return fe
        return _export


class aframe(animation):
    def __init__(self,
        rect=(1080, 1080),
        **kwargs
        ):
        super().__init__(rect,
            timeline=Timeline(1),
            **kwargs)


class FFMPEGExport():
    def __init__(self, a:animation,
        passes:list,
        date=False,
        loops=1):
        self.a = a
        self.passes = passes
        self.date = date
        self.loops = loops
        self.fmt = None

        passes = [p for p in self.passes if p.render == self.a]
        template = re.sub(r"[0-9]{4}\.png", "%4d.png", str(passes[0].output_path))
        #template = str(passes[0].output_path).replace("0000.png", "%4d.png")

        self.folder = passes[0].output_path.parent.parent

        # https://github.com/typemytype/drawbot/blob/master/drawBot/context/tools/mp4Tools.py
        self.args = [
            "ffmpeg",
            "-y", # overwrite existing files
            "-loglevel", "16", # 'error, 16' Show all errors
            "-r", str(self.a.timeline.fps),
            "-i", template, # input sequence
            "-filter_complex", f"loop=loop={self.loops-1}:size={self.a.timeline.duration}:start=0"
        ]
    
    def h264(self):
        self.fmt = "mp4"
        self.args.extend([
            "-c:v", "libx264",
            "-crf", "20", # Constant Rate Factor
            "-pix_fmt", "yuv420p", # pixel format
        ])
        return self
    
    def prores(self):
        # https://video.stackexchange.com/questions/14712/how-to-encode-apple-prores-on-windows-or-linux
        self.fmt = "mov"
        self.args.extend([
            "-c:v", "prores_ks",
            "-c:a", "pcm_s16le",
            "-profile:v", "2"
        ])
        return self
    
    def gif(self):
        self.fmt = "gif"
        #self.args.extend([])
        return self
    
    def write(self):
        if not self.fmt:
            raise Exception("No fmt specified")
        
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        d = ("_" + now) if self.date else ""
        self.output_path = self.folder / f"{self.a.name}{d}.{self.fmt}"

        self.args.append(self.output_path)
        print(self.args)
        run(self.args)

        print(">", self.output_path)
        return self
    
    def open(self):
        """i.e. Reveal-in-Finder"""
        os.system(f"open {self.output_path.parent}")
        return self