import math, os, re
from typing import Tuple

from subprocess import run
from pathlib import Path
from datetime import datetime

from coldtype.time.timeable import Timeable
from coldtype.time import Frame
from coldtype.time.timeline import Timeline

from coldtype.text.reader import Style, Font
from coldtype.runon.path import P
from coldtype.geometry import Rect, Point
from coldtype.color import bw, hsl

from coldtype.renderable.renderable import renderable, Action, RenderPass, Overlay


class animation(renderable, Timeable):
    """
    Base class for any frame-wise animation animatable by Coldtype
    """
    def __init__(self,
        rect=(1080, 1080),
        timeline:Timeline=10,
        show_frame=True,
        offset=0,
        overlay=True,
        audio=None,
        suffixer=None,
        **kwargs
        ):
        if "tl" in kwargs:
            timeline = kwargs["tl"]
            del kwargs["tl"]

        super().__init__(**kwargs)
        
        self.rect = Rect(rect).round()
        self.r = self.rect
        self.overlay = overlay
        self.start = 0
        self.offset = offset
        self.show_frame = show_frame
        self.reset_timeline(timeline)
        self.single_frame = self.duration == 1
        self.audio = audio
        self.suffixer = suffixer
    
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
    
    def folder(self, filepath):
        return filepath.stem + "/" + self.name # TODO necessary?
    
    def all_frames(self):
        return list(range(0, self.duration))
    
    def _active_frames(self, renderer_state):
        frames = []
        if renderer_state:
            frames.append((renderer_state.frame_offset + self.offset) % self.duration)
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
        idx = index % self.duration

        if self.suffixer:
            return self.suffixer(idx)
        elif self.suffix:
            pf = self.suffix + "_"
        else:
            pf = ""
        
        if isinstance(idx, int):
            return pf + "{:04d}".format(idx)
        else:
            return pf + index
    
    def passes(self, action, renderer_state, indices=[]):
        frames = self.active_frames(action, renderer_state, indices)
        return [RenderPass(self, action, i, [Frame(i, self)]) for i in frames]

    def running_in_viewer(self):
        return True
    
    def run(self, render_pass, renderer_state):
        fi = render_pass.args[0].i
        if renderer_state and self.running_in_viewer():
            if renderer_state.previewing:
                if Overlay.Rendered in renderer_state.overlays:
                    return self.frame_img(fi)
        
        self.t.hold(fi)
        return super().run(render_pass, renderer_state)
    
    def runpost(self, result, render_pass, renderer_state):
        #if Overlay.Rendered in renderer_state.overlays:
        #    from coldtype.img.skiaimage import SkiaImage
        #    return SkiaImage(render_pass.output_path)

        res = super().runpost(result, render_pass, renderer_state)

        if Overlay.Recording in renderer_state.overlays and self.overlay:
            res.append(P().oval(Point(0, 0).rect(30, 30)).f(hsl(0, 1, 0.7)))

        if Overlay.Info in renderer_state.overlays and self.overlay:
            t = self.rect.take(50, "mny")
            frame:Frame = render_pass.args[0]
            return P([
                res,
                P().rect(t).f(bw(0, 0.75)) if self.show_frame else None,
                P().text(f"{frame.i} / {self.duration}", Style("Times", 42, load_font=0, fill=bw(1)), t.inset(10)) if self.show_frame else None])
        return res
    
    def package(self):
        pass

    def fn_to_frame(self, fn_name):
        return 0
    
    def frame_to_fn(self, fi) -> Tuple[str, dict]:
        return None, {}
    
    def viewOffset(self, offset):
        @animation(self.rect, timeline=self.timeline, offset=offset, preview_only=1)
        def offset_view(f):
            return self.func(Frame(f.i, self))
        return offset_view

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
            
            dps = P()
            dps += P().rect(r).f(self.bg)
            for idx, g in enumerate(r.grid(gx, gy)):
                if idx < len(pngs):
                    dps += P().rect(g).f(None).img(pngs[idx], g, pattern=False)
            return dps
        
        return contactsheet
    
    def frame_img(self, fi):
        from coldtype.img.skiaimage import SkiaImage
        return SkiaImage(self.pass_path(fi))
    
    frameImg = frame_img
    
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
            "-r", str(self.a.timeline.fps)
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
                #"-stream_loop", str(self.loops-1),
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
        print(f"writing {self.fmt}...")

        if not self.fmt:
            raise Exception("No fmt specified")
        
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        d = ("_" + now) if self.date else ""
        self.output_path = self.folder / f"{self.a.name}{d}.{self.fmt}"

        self.args.append(self.output_path)
        if verbose:
            print(" ".join([str(s) for s in self.args]))
        run(self.args)

        if verbose:
            print(">", self.output_path)

        print("...done")
        return self
    
    def open(self):
        """i.e. Reveal-in-Finder"""
        os.system(f"open {self.output_path.parent}")
        return self


class fontpreview(animation):
    def __init__(self, font_re, font_dir=None, rect=(1200, 150), limit=25, **kwargs):
        self.dir = font_dir
        self.re = font_re
        self.matches = []

        for font in Font.List(self.re, self.dir):
            if re.search(self.re, str(font)):
                if len(self.matches) < limit:
                    self.matches.append(font)
        
        self.matches.sort()

        super().__init__(rect=rect, timeline=Timeline(len(self.matches)), **kwargs)
    
    def passes(self, action, renderer_state, indices=[]):
        frames = self.active_frames(action, renderer_state, indices)
        return [RenderPass(self, action, i, [Frame(i, self), self.matches[i]]) for i in frames]
