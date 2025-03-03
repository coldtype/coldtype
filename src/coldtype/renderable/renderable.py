import inspect, platform, re, tempfile, math, datetime

try:
    import skia
    from coldtype.pens.skiapen import SkiaPen
    from coldtype.pens.svgpen import SVGPen
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
from coldtype.img.abstract import AbstractImage


class Memory(object):
    def __init__(self, i, data) -> None:
        self.i = i
        self._keys = []
        
        if data:
            for k, v in data.items():
                self._keys.append(k)
                setattr(self, k, v)
    
    def add(self, k, v):
        if k not in self._keys:
            self._keys.append(k)
        setattr(self, k, v)
        return self

    def __eq__(self, other):
        equal = True
        for k in self.keys:
            if not equal:
                return False
            try:
                equal = getattr(self, k) == getattr(other, k)
            except:
                equal = False
        return equal


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
    PreviewOnce = "preview_play"
    PreviewIndices = "preview_indices"
    PreviewStoryboardNext = "preview_storyboard_next"
    PreviewStoryboardPrev = "preview_storyboard_prev"
    PreviewStoryboardNextMany = "preview_storyboard_next_many"
    PreviewStoryboardPrevMany = "preview_storyboard_prev_many"
    ClearLastRender = "clear_last_render"
    ClearRenderedFrames = "clear_rendered_frames"
    RestartRenderer = "restart_renderer"
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
        self.render_only = False
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
        return filepath.stem + "/" + self.name


class renderable():
    """
    Base class for any content renderable by Coldtype.
    """
    def __init__(self,
        rect=(1080, 1080),
        bg=None,
        fmt="png",
        name=None,
        rasterizer=None,
        prefix=None,
        suffix=None,
        dst=None,
        custom_folder=None,
        post_preview=None,
        watch=[],
        watch_soft=[],
        watch_restart=[],
        solo=False,
        mute=False,
        rstate=False,
        preview_only=False,
        preview_scale=1,
        render_only=False,
        direct_draw=False,
        clip=False,
        composites=False,
        single_frame=True,
        interactable=False,
        cv2caps=None,
        render_bg=True,
        style="_default",
        viewBox=True,
        layer=False,
        cond=None,
        sort=0,
        hide=[],
        grid=None,
        xray=True,
        memory=None,
        reset_memory=None):
        """Base configuration for a renderable function"""

        self.rect = Rect(rect).round()
        self._stacked_rect = None
        
        if bg is not None and bg != -1:
            if callable(bg):
                self.bg_fn = bg
                self.bg = None
            else:
                self.bg_fn = None
                self.bg = normalize_color(bg)
        else:
            self.bg_fn = None
            self.bg = None
        
        self.fmt = fmt
        self.prefix = prefix
        self.suffix = suffix
        self.dst = Path(dst).expanduser().resolve() if dst else None
        self.custom_folder = custom_folder
        self.post_preview = post_preview
        self.last_passes = []
        self.last_result = None
        self.style = style
        self.composites = composites
        self.single_frame = single_frame
        self.interactable = interactable
        self.cv2caps = cv2caps
        self.grid = grid
        self.xray = xray
        self.memory = memory
        self.reset_memory = reset_memory
        self._hide = hide

        self.watch = []
        for w in watch:
            self.add_watchee(w)
        
        self.watch_soft = []
        for w in watch_soft:
            self.watch_soft.append(self.add_watchee(w, "soft"))
        
        self.watch_restart = []
        for w in watch_restart:
            self.watch_restart.append(self.add_watchee(w, "restart"))

        self.cond = cond
        self.name = name
        self.codepath = None
        self.rasterizer = rasterizer
        self.self_rasterizing = False
        self.hidden = solo == -1
        self.solo = solo
        self.mute = mute
        self.preview_only = preview_only
        self.preview_scale = preview_scale
        self.render_only = render_only
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
    
    def choose(self, fields):
        rec = {}
        for f in fields:
            if hasattr(self, f):
                rec[f] = getattr(self, f)
        return rec
    
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
    
    def pass_img(self, index=0):
        from coldtype.img.skiaimage import SkiaImage
        return SkiaImage(self.pass_path(index=index))
    
    def passes(self, action, renderer_state, indices=[]):
        return [RenderPass(self, action, 0, [self.rect])]

    def package(self):
        pass

    def write_reset_memory(self, renderer_state, new_memory, overwrite, initial):
        if initial and renderer_state and not renderer_state.memory_initial:
            renderer_state.memory_initial = Memory(0, self.memory)

        if not renderer_state or not self.memory:
            return
        
        if renderer_state.memory and not overwrite:
            if initial:
                mi = renderer_state.memory_initial
                for k, v in self.memory.items():
                    if not hasattr(mi, k) or getattr(mi, k) != v:
                        renderer_state.memory_initial.add(k, v)
                        renderer_state.memory.add(k, v)
            return

        if not new_memory:
            new_memory = self.memory

        i = 0
        if renderer_state.memory and overwrite:
            i = renderer_state.memory.i
        
        if callable(new_memory):
            m = new_memory(i+1)
        else:
            m = new_memory

        renderer_state.memory = Memory(i+1, m)

    def run(self, render_pass, renderer_state, render_bg=True):
        self.write_reset_memory(renderer_state, self.memory, False, True)

        if self.rstate:
            res = render_pass.fn(*render_pass.args, renderer_state)
        elif self.memory:
            res = render_pass.fn(*render_pass.args, renderer_state.memory)
        else:
            res = render_pass.fn(*render_pass.args)
        
        if renderer_state:
            previewing = renderer_state.previewing
        else:
            previewing = False
        
        show_bg = (previewing or self.render_bg) and render_bg

        if show_bg:
            if self.bg_fn:
                if isinstance(self.bg_fn, type(self)):
                    from coldtype.img.skiaimage import SkiaImage
                    path = self.bg_fn.render_to_disk()[0]
                    return P(SkiaImage(path), res)
                else:
                    arg_count = len(inspect.signature(self.bg_fn).parameters)
                    args = [self.rect, render_pass]
                    return P([
                        self.bg_fn(*args[:arg_count]),
                        res
                    ])
            elif self.bg:
                return P([
                    P(self.rect).f(self.bg),
                    res
                ])
            else:
                return P(res)
        else:
            return P(res)
        
    def show_xray(self, result):
        if not self.xray:
            return result
        
        from coldtype.fx.xray import skeleton, hsl

        out = P()
        def xray(p, pos, _):
            if pos == 0:
                out.append(p.copy().ch(skeleton(0.5)))
        
        result.copy().walk(xray)
        return P(
            result.copy().fssw(-1, hsl(0.95, 1, 0.8), 4),
            out.fssw(-1, hsl(0.65, 1, 0.6), 2))
    
    def show_grid(self, result, settings):
        from coldtype.color import hsl, bw, Color

        invert_bg = self.bg.invert().with_alpha(0.5)
        grid = P().gridlines(self.rect).fssw(-1, invert_bg, 2)

        if self.grid is not None:
            if isinstance(self.grid, Color):
                g = {0:self.grid}
            else:
                g = {k:v for (k,v) in enumerate(self.grid)}
            grid = (P().gridlines(self.rect, g.get(2, 20), g.get(3, g.get(2, 20)))
                .fssw(-1, g.get(0, invert_bg), g.get(1, 2)))
        elif settings:
            g = {k:v for (k,v) in enumerate(settings)}
            grid = (P().gridlines(self.rect, g.get(2, 20), g.get(3, g.get(2, 20)))
                .fssw(-1, hsl(*g.get(0, invert_bg)), g.get(1, 2)))

        return P(result, grid)
    
    def runpost(self, result, render_pass:RenderPass, renderer_state, config):
        post_res = result
        if self.post_preview:
            post_res = self.post_preview(self, result)
        
        if config:
            if config.show_xray:
                post_res = self.show_xray(post_res)            
            if config.show_grid:
                post_res = self.show_grid(post_res, config.grid_settings)

        return post_res
    
    def precompose(self, result, scale):
        from coldtype.fx.skia import precompose
        return result.ch(precompose(self.rect, scale=scale, style=self.style))
    
    def postprocessor(self, result):
        has_post = result.find_(lambda el: el.data("postprocess") is not None, none_ok=True)
        if has_post:
            return has_post.data("postprocess")
        return None
    
    # def draw_preview(self, scale, canvas, rect, result, render_pass): # canvas:skia.Canvas
    #     sr = self.rect.scale(scale, "mnx", "mxx")
    #     SkiaPen.CompositeToCanvas(result, sr, canvas, scale, style=self.style)
    
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
        #import inspect
        normalized = self._normalize_result(pens)
        #print(">norm", self, pens, normalized)
        #curframe = inspect.currentframe()
        #calframe = inspect.getouterframes(curframe, 2)
        #print('caller name:', calframe[1])
        if self._hide:
            normalized.hide(*self._hide)
        return normalized
    
    def run_normal(self, render_pass, renderer_state=None, render_bg=True):
        return self.normalize_result(
            self.run(render_pass, renderer_state, render_bg=render_bg))
    
    def frame_result(self, fi, post=False, frame=False, render_bg=True):
        p = self.passes(None, None, [fi])[0]
        res = self.run_normal(p, None, render_bg=render_bg)
        if post:
            res = self.runpost(res, p, None, None)
        
        if frame:
            res.data(frame=self.rect)
        return res
    
    def rasterize(self, config, content, render_pass):
        return False
    
    def render_and_rasterize_frame(self, frame, scale=1, style=None) -> str:
        SkiaPen.Composite(self.normalize_result(self.frame_result(frame)),
            self.rect,
            str(self.pass_path(frame)),
            scale=scale,
            context=None,
            style=style)
        return self.pass_path(frame)
    
    def render_and_rasterize(self, scale=1, style=None) -> str:
        return self.render_and_rasterize_frame(0, scale=scale, style=style)
    
    def render_to_disk(self, print_paths=False, return_base64=False, return_text=False, render_bg=False, return_img=False):
        passes = self.passes(Action.RenderAll, None)
        paths = []
        for rp in passes:
            output_path = rp.output_path
            output_path.parent.mkdir(exist_ok=True, parents=True)

            if print_paths:
                print(output_path)
            
            result = self.run_normal(rp, None, render_bg)
            if self.fmt == "png":
                SkiaPen.Composite(result,
                    self.rect,
                    str(output_path),
                    scale=1,
                    context=None)
            elif self.fmt == "svg":
                output_path.write_text(SVGPen.Composite(result, self.rect, viewBox=self.viewBox))
            elif self.fmt == "pdf":
                SkiaPen.PDFOnePage(result, self.rect, output_path, 1)
            else:
                print("render_to_disk", self.fmt, "not supported")
            paths.append(output_path)

        if return_img:
            from coldtype.img.skiaimage import SkiaImage
            return [SkiaImage(p) for p in paths]
        elif return_base64:
            from base64 import b64encode
            return [str(b64encode(p.read_bytes()), encoding="utf-8") for p in paths]
        elif return_text:
            return [p.read_text() for p in paths]
        else:
            return paths
    
    def _profile_render_all(self):
        ps = self.passes(Action.RenderAll, None)
        for p in ps:
            self.run_normal(p)
        return self
    
    def profile(self, file="profile.profile"):
        import cProfile
        cProfile.runctx(f"self._profile_render_all()", {}, {"self": self}, filename=file)


class example(renderable):
    def __init__(self, rect=(800, 200), bg=1, **kwargs):
        super().__init__(rect=rect, bg=bg, **kwargs)


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