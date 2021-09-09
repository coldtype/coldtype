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
        storyboard=[0],
        timeline:Timeline=10,
        show_frame=True,
        overlay=True,
        write_start=0,
        **kwargs
        ):
        super().__init__(**kwargs)
        
        self.rect = Rect(rect).round()
        self.r = self.rect
        self.overlay = overlay
        self.start = 0
        self.show_frame = show_frame
        self.write_start = write_start
        self.storyboard = storyboard
        self.reset_timeline(timeline)
    
    def __call__(self, func):
        res = super().__call__(func)
        self.prefix = self.name + "_"
        return res

    def reset_timeline(self, timeline):
        if timeline is None:
            raise Exception("timeline= cannot be None")

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
        
        if self.write_start and self.storyboard == [0]:
            self.storyboard = [self.write_start]
    
    def folder(self, filepath):
        return filepath.stem + "/" + self.name # TODO necessary?
    
    def all_frames(self):
        return list(range(0, self.duration))
    
    def _active_frames(self, renderer_state):
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
        if hasattr(self.timeline, "workarea"):
            return list(self.timeline.workarea)
        elif hasattr(self.timeline, "workareas"):
            return list(self.timeline.workareas[0])
        else:
            return list(range(0, self.duration))
    
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
    
    def pass_suffix(self, index=0):
        if self.suffix:
            pf = self.suffix + "_"
        else:
            pf = ""
        
        if isinstance(index, int):
            idx = (index - self.write_start) % self.duration
            return pf + "{:04d}".format(idx)
        else:
            return pf + index
    
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
    
    def export(self, fmt, date=False, loops=1, open=1, audio=None, audio_loops=None, vf=None):
        def _export(passes):
            fe = FFMPEGExport(self, date=date, loops=loops, audio=audio, audio_loops=audio_loops, vf=vf)
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
        date=False,
        loops=1,
        audio=None,
        audio_loops=None,
        vf=None,
        ):
        self.a = a
        self.date = date
        self.loops = loops
        self.fmt = None
        if audio:
            self.audio = Path(audio).expanduser()
            self.audio_loops = audio_loops if audio_loops is not None else loops
            if not self.audio.exists():
                raise Exception("Audio file does not exist")
        else:
            self.audio = None
            self.audio_loops = loops

        template = a.pass_path(f"%4d.{a.fmt}")
        self.folder = template.parent.parent

        # https://github.com/typemytype/drawbot/blob/master/drawBot/context/tools/mp4Tools.py
        self.args = [
            "ffmpeg",
            "-y", # overwrite existing files
            "-loglevel", "16", # 'error, 16' Show all errors
            "-r", str(self.a.timeline.fps),
            "-stream_loop", str(self.loops-1),
            "-i", template, # input sequence
        ]

        if self.audio:
            self.args.extend([
                "-stream_loop", str(self.loops-1),
                "-i", template, # input sequence
                "-stream_loop", str(self.audio_loops-1),
                "-i", str(self.audio),
                #"-stream_loop", "-1",
            ])
        else:
            self.args.extend([
                "-i", template, # input sequence
                "-filter_complex", f"loop=loop={self.loops-1}:size={self.a.timeline.duration}:start=0"
            ])
        
        if vf:
           self.args.extend([
               "-vf", vf
           ])
    
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
    
    def write(self, verbose=False):
        if not self.fmt:
            raise Exception("No fmt specified")
        
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        d = ("_" + now) if self.date else ""
        self.output_path = self.folder / f"{self.a.name}{d}.{self.fmt}"

        self.args.append(self.output_path)
        if verbose or True:
            print(" ".join([str(s) for s in self.args]))
        run(self.args)

        if verbose:
            print(">", self.output_path)
        return self
    
    def open(self):
        """i.e. Reveal-in-Finder"""
        os.system(f"open {self.output_path.parent}")
        return self