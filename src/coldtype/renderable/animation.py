import math, os, re, json
from typing import Tuple

from subprocess import run
from pathlib import Path
from datetime import datetime

from coldtype.timing.timeable import Timeable
from coldtype.timing import Frame
from coldtype.timing.timeline import Timeline

from coldtype.text.reader import Style, Font
from coldtype.runon.path import P
from coldtype.geometry import Rect, Point
from coldtype.color import bw, hsl

from coldtype.renderable.renderable import renderable, Action, RenderPass, Overlay
from coldtype.osutil import show_in_finder


def raw_gifski(width, fps, frames, output_path, open=False):
    """simpler wrapper for already-installed gifski"""
    run([
        "gifski",
        "--fps", str(fps),
        "--width", str(width),
        "-o", output_path,
        *frames])
    print("\n")
    
    if open:
       show_in_finder(output_path.parent)
    return True


def gifski(a:"animation", passes, open=False):
    """simple wrapper for already-installed gifski"""
    root = a.pass_path(f"%4d.{a.fmt}").parent.parent
    gif = root / (a.name + ".gif")
    run([
        "gifski",
        "--fps", str(a.timeline.fps),
        "--width", str(a.rect.w),
        "-o", gif,
        *[p.output_path for p in passes if p.render == a]])
    print("\n")
    
    if open:
        show_in_finder(gif.parent)
    return gif


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
        clip_cursor=True,
        reset_to_zero=False,
        release=None,
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
        self.clip_cursor = clip_cursor
        self.reset_to_zero = reset_to_zero
        self.release = release
    
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
    
    def render_and_rasterize(self, scale=1, style=None) -> str:
        first = self.render_and_rasterize_frame(0, scale=scale, style=style)
        for idx in range(1, self.timeline.duration):
            print(">>>", idx)
            self.render_and_rasterize_frame(idx, scale=scale, style=style)
        return first
    
    def passes(self, action, renderer_state, indices=[]):
        c, m = None, None

        rp = self.recording_path
        recording = None
        has_recording = False

        if rp and rp.exists():
            has_recording = True
            recording = json.loads(rp.read_text())

        if renderer_state:
            c = renderer_state.cursor
            if self.clip_cursor:
                c = c.clip(self.rect)
            m = renderer_state.midi

            if Overlay.Recording in renderer_state.overlays and self.overlay and rp:
                if not has_recording:
                    recording = {"cursor":{}}

        frames = self.active_frames(action, renderer_state, indices)
        
        if renderer_state:
            if Overlay.Recording in renderer_state.overlays and self.overlay and rp:
                fi = frames[0]
                recording["cursor"][str(fi)] = [c.x, c.y]
                rp.write_text(json.dumps(recording))

        return [RenderPass(self, action, i, [Frame(i, self, c, m, recording)]) for i in frames]

    def running_in_viewer(self):
        return True
    
    def run(self, render_pass, renderer_state, render_bg=True):
        fi = render_pass.args[0].i
        if renderer_state and self.running_in_viewer():
            if renderer_state.previewing:
                if Overlay.Rendered in renderer_state.overlays:
                    return self.frame_img(fi)

        self.t.hold(fi)
        return super().run(render_pass, renderer_state, render_bg=render_bg)
    
    @property
    def recording_path(self):
        try:
            return self.filepath.parent / (self.filepath.stem + "_recording.json")
        except:
            return None
    
    def runpost(self, result, render_pass, renderer_state, config):
        res = super().runpost(result, render_pass, renderer_state, config)

        if Overlay.Recording in renderer_state.overlays and self.overlay and self.recording_path:
            t = self.rect.take(50, "mny")
            frame:Frame = render_pass.args[0]
            res.append(P().rect(Point(0, 0).rect(150, 60)).t(10, 10).f(hsl(0.95, 1, 0.7)))
            res.append(P().text(f"{frame.i}", Style("Courier", 42, load_font=0, fill=bw(1)), t.inset(10)))

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
    
    def contactsheet_renderable(self, scale=1, sl=slice(None, None, 1)):
        sheet = self.contactsheet(None, scale, sl)
        
        @renderable(sheet.data("frame"), bg=self.bg)
        def contactsheet(r):
            return sheet
        
        return contactsheet
    
    def contactsheet(self, r:Rect=None, scale=1, sl=slice(None, None, 1), border=True, grid=True, bgs=False):
        from coldtype.runon.scaffold import Scaffold

        xs = list(range(0, self.timeline.duration)[sl])
        sq = math.ceil(math.sqrt(len(xs)))

        if r is None:
            r = Rect(0, 0, sq*self.rect.w*scale, sq*self.rect.h*scale)

        s = Scaffold(r).grid(sq, sq)

        def frame(x):
            try:
                fi = xs[x.i]
                return (self
                    .frame_result(fi, frame=1, render_bg=bgs)
                    .align(x.el.rect, tx=0)
                    .scale(scale, tx=0))
            except IndexError:
                return None
        
        return P(
            P(s.r).tag("border").fssw(-1, 0, 1) if border else None,
            s.borders().tag("grid").fssw(-1, 0, 1) if grid else None,
            P().enumerate(s, frame).tag("frames")
        ).data(frame=r)
    
    def frame_img(self, fi):
        from coldtype.img.skiaimage import SkiaImage
        return SkiaImage(self.pass_path(fi))
    
    frameImg = frame_img
    
    def export(self, fmt, date=False, loops=1, open=1, audio=None, audio_loops=None, vf=None, set_709=True):
        def _export(passes):
            fe = FFMPEGExport(self, date=date, loops=loops, audio=audio or self.audio, audio_loops=audio_loops, vf=vf, set_709=set_709)
            if fmt == "gif":
                fe.gif()
            elif fmt == "h264":
                fe.h264()
            elif fmt == "prores":
                fe.prores()
            print(fe.args)
            fe.write()
            if open:
                fe.open()
            return fe
        return _export
    
    def gifski(self, open=False):
        def _gifski(passes):
            return gifski(self, passes, open=open)
        return _gifski


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
        output_folder=None,
        vf=None,
        set_709=True,
        ):
        self.a = a
        self.date = date
        self.loops = loops
        self.fmt = None
        self.failed = False
        self.set_709 = set_709
        
        if audio:
            self.audio = Path(audio).expanduser()
            self.audio_loops = audio_loops if audio_loops is not None else loops
            if not self.audio.exists():
                raise Exception("Audio file does not exist")
        else:
            self.audio = None
            self.audio_loops = loops
        
        template = a.pass_path(f"%4d.{a.fmt}")

        if output_folder is not None:
            self.output_folder = output_folder
        else:
            self.output_folder = template.parent.parent

        # https://github.com/typemytype/drawbot/blob/master/drawBot/context/tools/mp4Tools.py

        from coldtype.renderable.tools import FFMPEG_COMMAND
        print("> ffmpeg command ==", FFMPEG_COMMAND)

        self.args = [
            FFMPEG_COMMAND,
            "-y", # overwrite existing files
            "-loglevel", "16", # 'error, 16' Show all errors
            "-r", str(self.a.timeline.fps)
        ]

        if self.set_709:
            set_709 = "zscale=matrixin=709:transferin=709:primariesin=709:matrix=709:transfer=709:primaries=709,"
        else:
            set_709 = ""

        if self.audio:
            self.args.extend([
                "-stream_loop", str(self.loops-1),
                "-i", template, # input sequence
                "-stream_loop", str(self.audio_loops-1),
                "-i", str(self.audio),
                #"-stream_loop", "-1",
                "-filter_complex", f"[0:v]loop=loop=0:size={self.a.timeline.duration}:start=0,{set_709}format=yuv420p[v]",
                "-map", '[v]',
                "-map", "1:a",
            ])
        else:
            self.args.extend([
                #"-stream_loop", str(self.loops-1),
                "-i", template, # input sequence
                "-filter_complex", f"[0:v]loop=loop={self.loops-1}:size={self.a.timeline.duration}:start=0,{set_709}format=yuv420p[v]",
                "-map", '[v]',
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
            #"", "",
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
    
    def write(self, verbose=False, name=None):
        first_frame = self.a.pass_path(0)
        if not Path(first_frame).exists():
            self.failed = True
            print("! Need to render before release")
            return self

        print(f"writing {self.fmt}...")

        if not self.fmt:
            raise Exception("No fmt specified")
        
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        d = ("_" + now) if self.date else ""

        if name is None:
            name = self.a.name
        
        self.output_path = self.output_folder / f"{name}{d}.{self.fmt}"

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
        if self.failed:
            return self
        show_in_finder(self.output_path.parent)
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


import shutil
try:
    from coldtype.img.skiaimage import SkiaImage
except ImportError:
    SkiaImage = None


class image_sequence(animation):
    """
    Preview pre-rendered image-based animations;
    move images into renders folder with shutil.copy
    (good for something like making a prores file from
    an image sequence (if you use the FFMPEGExport))
    """
    def __init__(self, images, fps, looping=False, loops=1, **kwargs):
        self.images = images
        self.looping = looping

        if self.looping:
            timeline = Timeline(len(self.images)*2-2, fps)
        else:
            timeline = Timeline(len(self.images), fps)
        
        img = SkiaImage(self.images[0])
        super().__init__(img.rect(), timeline, fmt=self.images[0].suffix[1:], **kwargs)
        self.self_rasterizing = True
    
    def normalize_result(self, pens):
        return pens
    
    def run(self, render_pass, renderer_state):
        from coldtype.timing.easing import ez

        idx = render_pass.idx
        if self.looping:
            t = idx/self.timeline.duration
            idx = round(ez(t, "l", 1, rng=(0, len(self.images)-1)))
        
        result = None
        if renderer_state and renderer_state.previewing:
            return self.images[idx]
        else:
            render_pass.output_path.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy(self.images[idx], render_pass.output_path)
            result = render_pass.output_path
        return result


try:
    import skia
except ImportError:
    skia = None

class skia_direct_animation(animation):
    def __init__(self, rect=(1080, 1080), **kwargs):
        super().__init__(rect=rect, direct_draw=True, **kwargs)
    
    def run(self, render_pass, renderer_state, canvas=None):
        if canvas is None:
            surface = skia.Surface(*self.rect.wh())
            with surface as canvas:
                render_pass.fn(*render_pass.args, canvas)
            return

        if self.rstate:
            return render_pass.fn(*render_pass.args, renderer_state, canvas)
        else:
            return render_pass.fn(*render_pass.args, canvas)