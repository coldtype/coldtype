import inspect, platform, re, tempfile, math, datetime

try:
    import skia
    from coldtype.pens.skiapen import SkiaPen
except ImportError:
    skia = None
    SkiaPen = None

from enum import Enum
from subprocess import run
from pathlib import Path

from coldtype.geometry import Rect, Point
from coldtype.color import normalize_color
from coldtype.text.reader import normalize_font_prefix, Font
from coldtype.runon.path import P
from coldtype.img.datimage import DATImage

class ColdtypeCeaseConfigException(Exception):
    pass

class Overlay(Enum):
    Info = "info"
    Timeline = "timeline"
    Rendered = "rendered"
    Recording = "recording"

class Action(Enum):
    Initial = "initial"
    Resave = "resave"
    RenderAll = "render_all"
    RenderWorkarea = "render_workarea"
    RenderIndices = "render_indices"
    Build = "build"
    Release = "release"
    PreviewStoryboard = "preview_storyboard"
    PreviewStoryboardReload = "preview_storyboard_reload"
    PreviewPlay = "preview_play"
    PreviewIndices = "preview_indices"
    PreviewStoryboardNext = "preview_storyboard_next"
    PreviewStoryboardPrev = "preview_storyboard_prev"
    PreviewStoryboardNextMany = "preview_storyboard_next_many"
    PreviewStoryboardPrevMany = "preview_storyboard_prev_many"
    ClearLastRender = "clear_last_render"
    ClearRenderedFrames = "clear_rendered_frames"
    RestartRenderer = "restart_renderer"
    ToggleMultiplex = "toggle_multiplex"
    Kill = "kill"


class RenderPass():
    def __init__(self, render:"renderable", action, idx, args):
        self.render = render
        self.action = action
        self.fn = self.render.func
        self.args = args
        self.path = None
        
        self.idx = idx
        self.prefix = render.pass_prefix()
        self.output_path = render.pass_path(index=idx)
        #self.output_path = render.output_folder / f"{self.prefix}{self.suffix}.{render.fmt}"

        self.i = None
        if hasattr(args[0], "i"):
            self.i = args[0].i
    
    def __repr__(self):
        return f"<RenderPass:f{self.output_path}/>"


class runnable():
    """Minimal interface for runnable code in an abstract context (like a renderable but with nothing to render)"""
    def __init__(self, solo=False, cond=None):
        self.filepath = None
        self.codepath = None
        self.hidden = solo == -1
        self.solo = solo
        self.preview_only = True
        self.dst = None
        self.custom_folder = None
        self.name = None
        self.sort = 0
        self.cv2caps = None
        self.watch = []
        self.cond = cond
    
    def __call__(self, func):
        self.func = func
        if not self.name:
            self.name = self.func.__name__
        return self
    
    def post_read(self):
        pass
    
    def run(self):
        return self.func()
    
    def folder(self, filepath):
        return ""


class renderable():
    """
    Base class for any content renderable by Coldtype
    """
    def __init__(self,
        rect=(1080, 1080),
        bg="whitesmoke",
        fmt="png",
        name=None,
        rasterizer=None,
        prefix=None,
        suffix=None,
        dst=None,
        custom_folder=None,
        postfn=None,
        watch=[],
        watch_soft=[],
        solo=False,
        rstate=False,
        preview_only=False,
        direct_draw=False,
        clip=False,
        composites=False,
        single_frame=True,
        interactable=False,
        cv2caps=None,
        render_bg=False,
        style="_default",
        viewBox=True,
        layer=False,
        cond=None,
        sort=0,
        hide=[]):
        """Base configuration for a renderable function"""

        self.rect = Rect(rect).round()
        self._stacked_rect = None

        self.bg = normalize_color(bg)
        self.fmt = fmt
        self.prefix = prefix
        self.suffix = suffix
        self.dst = Path(dst).expanduser().resolve() if dst else None
        self.custom_folder = custom_folder
        self.postfn = postfn
        self.last_passes = []
        self.last_result = None
        self.style = style
        self.composites = composites
        self.single_frame = single_frame
        self.interactable = interactable
        self.cv2caps = cv2caps
        self._hide = hide

        self.watch = []
        for w in watch:
            self.add_watchee(w)
        
        self.watch_soft = []
        for w in watch_soft:
            self.watch_soft.append(self.add_watchee(w, "soft"))

        self.cond = cond
        self.name = name
        self.codepath = None
        self.rasterizer = rasterizer
        self.self_rasterizing = False
        self.hidden = solo == -1
        self.solo = solo
        self.preview_only = preview_only
        self.rstate = rstate
        self.clip = clip
        self.viewBox = viewBox
        self.direct_draw = direct_draw
        self.render_bg = render_bg
        self.sort = sort
        self.layer = layer
        if self.layer:
            self.bg = normalize_color(None)
        
        self.filepath = None

        if not rasterizer:
            if self.fmt == "svg":
                self.rasterizer = "svg"
            elif self.fmt == "pickle":
                self.rasterizer = "pickle"
            else:
                self.rasterizer = "skia"
    
    def post_read(self):
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}/>"
    
    def add_watchee(self, w, flag=None):
        try:
            pw = Path(w).expanduser().resolve()
            if not pw.exists():
                print(w, "<<< does not exist (cannot be watched)")
            else:
                self.watch.append([pw, flag])
                return pw
        except TypeError:
            if isinstance(w, Font):
                self.watch.append([w, flag])
            else:
                raise Exception("Can only watch path strings, Paths, and Fonts")
    
    def __call__(self, func):
        self.func = func
        if not self.name:
            self.name = self.func.__name__
        self.output_folder = Path(f"renders/{self.name}")
        return self
    
    def folder(self, filepath):
        return ""
    
    def pass_suffix(self, index=0):
        return self.name
    
    def pass_prefix(self):
        if self.prefix is None:
            if self.filepath is not None:
                prefix = f"{self.filepath.stem}_"
            else:
                prefix = None
        else:
            prefix = self.prefix
        return prefix
    
    def pass_path(self, index=0):
        if index is None:
            return self.output_folder / f"{self.pass_prefix()}"
        elif isinstance(index, int):
            return self.output_folder / f"{self.pass_prefix()}{self.pass_suffix(index)}.{self.fmt}"
        else:
            return self.output_folder / f"{self.pass_prefix()}{self.pass_suffix(index)}"
    
    def passes(self, action, renderer_state, indices=[]):
        return [RenderPass(self, action, 0, [self.rect])]

    def package(self):
        pass

    def run(self, render_pass, renderer_state):
        if self.rstate:
            res = render_pass.fn(*render_pass.args, renderer_state)
        else:
            res = render_pass.fn(*render_pass.args)
        
        if self.render_bg:
            return P([
                P(self.rect).f(self.bg),
                res
            ])
        else:
            return res
    
    def runpost(self, result, render_pass, renderer_state):
        if self.postfn:
            return self.postfn(self, result)
        else:
            return result
    
    def draw_preview(self, scale, canvas, rect, result, render_pass): # canvas:skia.Canvas
        sr = self.rect.scale(scale, "mnx", "mxx")
        SkiaPen.CompositeToCanvas(result, sr, canvas, scale, style=self.style)
    
    def noop(self, *args, **kwargs):
        return self
    
    def hide(self):
        self.hidden = True
        return self
    
    def _hide(self):
        self.hidden = False
        return self
    
    def show(self):
        self.hidden = False
        return self
    
    def _normalize_result(self, pens):
        if not pens:
            return P()
        elif not isinstance(pens, P):
            return P(pens)
        else:
            return pens
    
    def normalize_result(self, pens):
        normalized = self._normalize_result(pens)
        #print(">norm", pens, normalized)
        if self._hide:
            normalized.hide(*self._hide)
        return normalized
    
    def run_normal(self, render_pass, renderer_state=None):
        return self.normalize_result(
            self.run(render_pass, renderer_state))
    
    def frame_result(self, fi, post=False):
        p = self.passes(None, None, [fi])[0]
        res = self.run_normal(p, None)
        if post:
            return self.runpost(res, p, None)
        else:
            return res
    
    def rasterize(self, config, content, render_pass):
        return False
    
    def _profile_render_all(self):
        ps = self.passes(Action.RenderAll, None)
        for p in ps:
            self.run_normal(p)
        return self
    
    def profile(self, file="profile.profile"):
        import cProfile
        cProfile.runctx(f"self._profile_render_all()", {}, {"self": self}, filename=file)


class skia_direct(renderable):
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


# class glyph(renderable):
#     def __init__(self, glyphName, width=500, **kwargs):
#         r = Rect(kwargs.get("rect", Rect(1000, 1000)))
#         kwargs.pop("rect", None)
#         self.width = width
#         self.body = r.take(750, "mdy").take(self.width, "mdx")
#         self.glyphName = glyphName
#         super().__init__(rect=r, **kwargs)
    
#     def passes(self, action, renderer_state, indices=[]):
#         return [RenderPass(self, action, self.glyphName, [])]


class iconset(renderable):
    valid_sizes = [16, 32, 64, 128, 256, 512, 1024]

    def __init__(self, sizes=[128, 1024], **kwargs):
        super().__init__(**kwargs)
        self.sizes = sizes
    
    def folder(self, filepath):
        return f"{filepath.stem}_source"
    
    def passes(self, action, renderer_state, indices=[]): # TODO could use the indices here
        sizes = self.sizes
        if action == Action.RenderAll:
            sizes = self.valid_sizes
        return [RenderPass(self, action, str(size), [self.rect, size]) for size in sizes]
    
    def package(self):
        # inspired by https://retifrav.github.io/blog/2018/10/09/macos-convert-png-to-icns/
        iconset = self.output_folder.parent / f"{self.filepath.stem}.iconset"
        iconset.mkdir(parents=True, exist_ok=True)

        system = platform.system()
        
        if system == "Darwin":
            for png in self.output_folder.glob("*.png"):
                d = int(png.stem.split("_")[1])
                for x in [1, 2]:
                    if x == 2 and d == 16:
                        continue
                    elif x == 1:
                        fn = f"icon_{d}x{d}.png"
                    elif x == 2:
                        fn = f"icon_{int(d/2)}x{int(d/2)}@2x.png"
                    print(fn)
                run(["sips", "-z", str(d), str(d), str(png), "--out", str(iconset / fn)])
            run(["iconutil", "-c", "icns", str(iconset)])
        
        if True: # can be done windows or mac
            from PIL import Image
            output = self.output_folder.parent / f"{self.filepath.stem}.ico"
            largest = list(self.output_folder.glob("*_1024.png"))[0]
            img = Image.open(str(largest))
            icon_sizes = [(x, x) for x in self.valid_sizes]
            img.save(str(output), sizes=icon_sizes)