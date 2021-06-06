import inspect, platform, re, tempfile, math, datetime

from coldtype.pens.draftingpens import DraftingPens

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
from coldtype.pens.datpen import DATPen, DATPens
from coldtype.pens.dattext import DATText
from coldtype.img.datimage import DATImage

try:
    import drawBot as db
    import AppKit
except ImportError:
    db = None

class Keylayer(Enum):
    Default = 0
    Cmd = 1
    Editing = 2
    Text = 3

class Overlay(Enum):
    Info = "info"
    Timeline = "timeline"

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
    RenderedPlay = "rendered_play"
    ArbitraryTyping = "arbitrary_typing"
    ArbitraryCommand = "arbitrary_command"
    RestartRenderer = "restart_renderer"
    ToggleMultiplex = "toggle_multiplex"
    Kill = "kill"


class RenderPass():
    def __init__(self, render, suffix, args):
        self.render = render
        self.fn = self.render.func
        self.args = args
        self.suffix = suffix
        self.path = None
        self.output_path = None
    
    def __repr__(self):
        return f"<RenderPass:f{self.output_path}/>"


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
        watch_restarts=[],
        watch_soft=[],
        solo=False,
        rstate=False,
        preview_only=False,
        direct_draw=False,
        clip=False,
        composites=False,
        cv2caps=None,
        bg_render=False,
        style="default",
        viewBox=True,
        layer=False):
        """Base configuration for a renderable function"""

        self.rect = Rect(rect).round()
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
        self.cv2caps = cv2caps

        self.watch = []
        for w in watch:
            self.add_watchee(w)

        self.watch_restarts = []
        for w in watch_restarts:
            self.watch_restarts.append(self.add_watchee(w, "restart"))
        
        self.watch_soft = []
        for w in watch_soft:
            self.watch_soft.append(self.add_watchee(w, "soft"))

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
        self.bg_render = bg_render
        self.layer = layer
        if self.layer:
            self.bg = normalize_color(None)

        if not rasterizer:
            if self.fmt == "svg":
                self.rasterizer = "svg"
            elif self.fmt == "pickle":
                self.rasterizer = "pickle"
            else:
                self.rasterizer = "skia"
    
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
        return self
    
    def folder(self, filepath):
        return ""
    
    def pass_suffix(self):
        return self.name
    
    def passes(self, action, renderer_state, indices=[]):
        return [RenderPass(self, self.pass_suffix(), [self.rect])]

    def package(self, filepath, output_folder):
        pass

    def run(self, render_pass, renderer_state):
        if self.rstate:
            return render_pass.fn(*render_pass.args, renderer_state)
        else:
            return render_pass.fn(*render_pass.args)
    
    def runpost(self, result, render_pass, renderer_state):
        if self.postfn:
            return self.postfn(self, result)
        else:
            return result
    
    def draw_preview(self, scale, canvas, rect, result, render_pass): # canvas:skia.Canvas
        sr = self.rect.scale(scale, "mnx", "mxx")
        SkiaPen.CompositeToCanvas(result, sr, canvas, scale, style=self.style)
    
    def hide(self):
        self.hidden = True
        return self
    
    def show(self):
        self.hidden = False
        return self
    
    def normalize_result(self, pens):
        if not pens:
            return DATPens()
        elif hasattr(pens, "_pens"):
            if (isinstance(pens, DraftingPens)
                and not isinstance(pens, DATPens)):
                return DATPens(pens._pens)
            return pens
        elif isinstance(pens, DATPen):
            return DATPens([pens])
        elif isinstance(pens, DATText):
            return DATPens([pens])
        elif isinstance(pens, DATImage):
            return DATPens([pens])
        elif not isinstance(pens, DATPens):
            return DATPens(pens)
        else:
            return pens


class skia_direct(renderable):
    def __init__(self, rect=(1080, 1080), **kwargs):
        super().__init__(rect=rect, direct_draw=True, **kwargs)
    
    def run(self, render_pass, renderer_state, canvas):
        if self.rstate:
            return render_pass.fn(*render_pass.args, renderer_state, canvas)
        else:
            return render_pass.fn(*render_pass.args, canvas)


class drawbot_script(renderable):
    def __init__(self, rect=(1080, 1080), scale=1, **kwargs):
        if not db:
            raise Exception("DrawBot not installed!")
        super().__init__(rect=Rect(rect).scale(scale), rasterizer="drawbot", **kwargs)
        self.self_rasterizing = True
    
    def normalize_result(self, pens):
        return pens
    
    def run(self, render_pass, renderer_state):
        from coldtype.pens.drawbotpen import DrawBotPen
        use_pool = True
        if use_pool:
            pool = AppKit.NSAutoreleasePool.alloc().init()
        try:
            db.newDrawing()
            if renderer_state.previewing:
                ps = renderer_state.preview_scale
                db.size(self.rect.w*ps, self.rect.h*ps)
                db.scale(ps, ps)
                DATPen().rect(self.rect).f(self.bg).cast(DrawBotPen).draw()
            else:
                db.size(self.rect.w, self.rect.h)
            if self.rstate:
                render_pass.fn(*render_pass.args, renderer_state)
            else:
                render_pass.fn(*render_pass.args)
            result = None
            if renderer_state.previewing:
                previews = (render_pass.output_path.parent / "_previews")
                previews.mkdir(exist_ok=True, parents=True)
                preview_frame = previews / render_pass.output_path.name
                db.saveImage(str(preview_frame))
                result = preview_frame
            else:
                render_pass.output_path.parent.mkdir(exist_ok=True, parents=True)
                db.saveImage(str(render_pass.output_path))
                result = render_pass.output_path
            db.endDrawing()
        finally:
            if use_pool:
                del pool
        return result


class svgicon(renderable):
    def __init__(self, **kwargs):
        super().__init__(fmt="svg", **kwargs)
    
    def folder(self, filepath):
        return filepath.stem


class glyph(renderable):
    def __init__(self, glyphName, width=500, **kwargs):
        r = Rect(kwargs.get("rect", Rect(1000, 1000)))
        kwargs.pop("rect", None)
        self.width = width
        self.body = r.take(750, "mdy").take(self.width, "mdx")
        self.glyphName = glyphName
        super().__init__(rect=r, **kwargs)
    
    def passes(self, action, renderer_state, indices=[]):
        return [RenderPass(self, self.glyphName, [])]


class fontpreview(renderable):
    def __init__(self, font_dir, font_re, rect=(1200, 150), limit=25, **kwargs):
        super().__init__(rect=rect, **kwargs)
        self.dir = normalize_font_prefix(font_dir)
        self.re = font_re
        self.matches = []
        
        for font in self.dir.iterdir():
            if re.search(self.re, str(font)):
                if len(self.matches) < limit:
                    self.matches.append(font)
        
        self.matches.sort()
    
    def passes(self, action, renderer_state, indices=[]):
        return [RenderPass(self, "{:s}".format(m.name), [self.rect, m]) for m in self.matches]


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
        return [RenderPass(self, str(size), [self.rect, size]) for size in sizes]
    
    def package(self, filepath, output_folder):
        # inspired by https://retifrav.github.io/blog/2018/10/09/macos-convert-png-to-icns/
        iconset = output_folder.parent / f"{filepath.stem}.iconset"
        iconset.mkdir(parents=True, exist_ok=True)

        system = platform.system()
        
        if system == "Darwin":
            for png in output_folder.glob("*.png"):
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
            output = output_folder.parent / f"{filepath.stem}.ico"
            largest = list(output_folder.glob("*_1024.png"))[0]
            img = Image.open(str(largest))
            icon_sizes = [(x, x) for x in self.valid_sizes]
            img.save(str(output), sizes=icon_sizes)