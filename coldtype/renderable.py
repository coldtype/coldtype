import inspect, platform, re, tempfile, skia, math

from enum import Enum
from subprocess import run
from pathlib import Path

from coldtype.geometry import Rect, Point
from coldtype.color import normalize_color
from coldtype.animation import Timeable, Frame
from coldtype.animation.timeline import Timeline
from coldtype.text.reader import normalize_font_prefix
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.pens.svgpen import SVGPen
from coldtype.pens.skiapen import SkiaPen

try:
    import drawBot as db
    import AppKit
except ImportError:
    db = None


class Action(Enum):
    Initial = "initial"
    Resave = "resave"
    RenderAll = "render_all"
    RenderWorkarea = "render_workarea"
    RenderIndices = "render_indices"
    Release = "release"
    PreviewStoryboard = "preview_storyboard"
    PreviewStoryboardReload = "preview_storyboard_reload"
    PreviewPlay = "preview_play"
    PreviewIndices = "preview_indices"
    PreviewStoryboardNext = "preview_storyboard_next"
    PreviewStoryboardPrev = "preview_storyboard_prev"
    RenderedPlay = "rendered_play"
    ArbitraryTyping = "arbitrary_typing"
    ArbitraryCommand = "arbitrary_command"
    SaveControllers = "save_controllers"
    ClearControllers = "clear_controllers"
    ResetControllers = "reset_controllers"
    RestartRenderer = "restart_renderer"
    ToggleMultiplex = "toggle_multiplex"
    Kill = "kill"


class WatchablePath():
    def __init__(self, path_str):
        if isinstance(path_str, str):
            self.path = Path(path_str).expanduser().absolute()
        else:
            self.path = path_str.expanduser().absolute()


class RenderPass():
    def __init__(self, render, suffix, args):
        self.render = render
        self.fn = self.render.func
        self.args = args
        self.suffix = suffix
        self.path = None
        self.single_layer = None
        self.output_path = None
    
    def __repr__(self):
        return f"<RenderPass:f{self.output_path}/>"


class renderable():
    def __init__(self,
        rect=(1080, 1080),
        bg="whitesmoke",
        fmt="png",
        rasterizer=None,
        prefix=None,
        dst=None,
        custom_folder=None,
        postfn=None,
        watch=[],
        layers=[],
        solo=False,
        rstate=False,
        preview_only=False,
        viewBox=True):
        """Base configuration for a renderable function"""

        self.rect = Rect(rect)
        self.bg = normalize_color(bg)
        self.fmt = fmt
        self.prefix = prefix
        self.dst = Path(dst).expanduser().resolve() if dst else None
        self.custom_folder = custom_folder
        self.postfn = postfn
        self.watch = [Path(w).expanduser().resolve() for w in watch]
        self.rasterizer = rasterizer
        self.self_rasterizing = False
        self.layers = layers
        self.hidden = solo == -1
        self.solo = solo
        self.preview_only = preview_only
        self.rstate = rstate
        self.viewBox = viewBox

        if not rasterizer:
            if self.fmt == "svg":
                self.rasterizer = "svg"
            elif self.fmt == "pickle":
                self.rasterizer = "pickle"
            else:
                self.rasterizer = "skia"
    
    def __call__(self, func):
        self.func = func
        return self
    
    def folder(self, filepath):
        return ""
    
    def layer_folder(self, filepath, layer):
        return ""
    
    def passes(self, action, layers, indices=[]):
        return [RenderPass(self, self.func.__name__, [self.rect])]

    def package(self, filepath, output_folder):
        pass

    def run(self, render_pass, renderer_state):
        if self.rstate:
            return render_pass.fn(*render_pass.args, renderer_state)
        else:
            return render_pass.fn(*render_pass.args)
    
    def runpost(self, result, render_pass):
        if self.postfn:
            return self.postfn(self, result)
        else:
            return result
    
    def draw_preview(self, scale, canvas:skia.Canvas, rect, result, render_pass):
        sr = self.rect.scale(scale, "mnx", "mxx")
        SkiaPen.CompositeToCanvas(result, sr, canvas, scale)
    
    def hide(self):
        self.hidden = True
        return self
    
    def show(self):
        self.hidden = False
        return self


class drawbot_script(renderable):
    def __init__(self, rect=(1080, 1080), scale=1, **kwargs):
        if not db:
            raise Exception("DrawBot not installed!")
        super().__init__(rect=Rect(rect).scale(scale), rasterizer="drawbot", **kwargs)
        self.self_rasterizing = True
    
    def run(self, render_pass, renderer_state):
        use_pool = True
        if use_pool:
            pool = AppKit.NSAutoreleasePool.alloc().init()
        try:
            db.newDrawing()
            db.size(self.rect.w, self.rect.h)
            render_pass.fn(*render_pass.args)
            result = None
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
    
    def passes(self, action, layers, indices=[]):
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
    
    def passes(self, action, layers, indices=[]):
        return [RenderPass(self, "{:s}".format(m.name), [self.rect, m]) for m in self.matches]


class iconset(renderable):
    valid_sizes = [16, 32, 64, 128, 256, 512, 1024]

    def __init__(self, sizes=[128, 1024], **kwargs):
        super().__init__(**kwargs)
        self.sizes = sizes
    
    def folder(self, filepath):
        return f"{filepath.stem}_source"
    
    def passes(self, action, layers, indices=[]): # TODO could use the indices here
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


class animation(renderable, Timeable):
    def __init__(self, rect=(1080, 1080), duration=10, storyboard=[0], timeline:Timeline=None, **kwargs):
        super().__init__(**kwargs)
        self.rect = Rect(rect)
        self.r = self.rect
        self.start = 0
        self.end = duration
        #self.duration = duration
        self.storyboard = storyboard
        if timeline:
            self.timeline = timeline
            self.t = timeline
            self.start = timeline.start
            self.end = timeline.end
            #self.duration = timeline.duration
            if self.storyboard != [0] and timeline.storyboard == [0]:
                pass
            else:
                self.storyboard = timeline.storyboard
        else:
            self.timeline = Timeline(30)
    
    def __call__(self, func):
        self.prefix = func.__name__
        return super().__call__(func)
    
    def folder(self, filepath):
        return filepath.stem + "/" + self.func.__name__ # TODO necessary?
    
    def layer_folder(self, filepath, layer):
        return layer
    
    def all_frames(self):
        return list(range(0, self.duration))
    
    def active_frames(self, action, layers, indices):
        frames = self.storyboard
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
        return frames
    
    def workarea(self):
        return list(self.timeline.workareas[0])
    
    def passes(self, action, layers, indices=[]):
        frames = self.active_frames(action, layers, indices)
        return [RenderPass(self, "{:04d}".format(i), [Frame(i, self, layers)]) for i in frames]
    
    def package(self, filepath, output_folder):
        pass
    
    def make_gif(self, passes):
        import imageio
        path = str(self.output_folder) + "_animation.gif"
        with imageio.get_writer(path, mode="I") as writer:
            for p in passes:
                if p.render == self:
                    image = imageio.imread(str(p.output_path))
                    writer.append_data(image)
        print(">>> wrote gif to", path)

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
        
        @renderable(rect=(ar.w*gx, ar.h*gy), bg=self.bg)
        def contactsheet(r:Rect):
            _pngs = list(sorted(self.output_folder.glob("*.png")))
            if sliced:
                pngs = _pngs[sl]
            else:
                pngs = [p for i, p in enumerate(_pngs) if i in sl]
            
            dps = DATPenSet()
            dps += DATPen().rect(r).f(self.bg)
            for idx, g in enumerate(r.grid(columns=gx, rows=gy)):
                if idx < len(pngs):
                    dps += DATPen().rect(g).f(None).attr(image=dict(src=pngs[idx], pattern=False))
            return dps
        
        contactsheet.func.__name__ = self.func.__name__ + "_contact"
        return contactsheet


class drawbot_animation(drawbot_script, animation):
    def passes(self, action, layers, indices=[]):
        if action in [
            Action.RenderAll,
            Action.RenderIndices,
            Action.RenderWorkarea]:
            frames = super().active_frames(action, layers, indices)
            passes = []
            for layer in layers:
                for i in frames:
                    p = RenderPass(self, "{:04d}".format(i), [Frame(i, self, [layer])])
                    p.single_layer = layer
                    passes.append(p)
            return passes
        else:
            return super().passes(action, layers, indices)