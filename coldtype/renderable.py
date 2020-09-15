import inspect, platform, re, tempfile

from enum import Enum
from subprocess import run
from pathlib import Path

from coldtype.geometry import Rect
from coldtype.color import normalize_color
from coldtype.animation import Timeable, Frame
from coldtype.animation.timeline import Timeline
from coldtype.text.reader import normalize_font_prefix
from coldtype.pens.svgpen import SVGPen

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
    PreviewStoryboard = "preview_storyboard"
    PreviewIndices = "preview_indices"
    PreviewStoryboardNext = "preview_storyboard_next"
    PreviewStoryboardPrev = "preview_storyboard_prev"
    ArbitraryTyping = "arbitrary_typing"
    ArbitraryCommand = "arbitrary_command"
    UICallback = "ui_callback"
    RestartRenderer = "restart_renderer"


class RenderPass():
    def __init__(self, render, suffix, args):
        self.render = render
        self.fn = self.render.func
        self.args = args
        self.suffix = suffix
        self.path = None
        self.single_layer = None


class renderable():
    def __init__(self, rect=(1080, 1080), bg="whitesmoke", hide=False, fmt="png", rasterizer=None, prefix=None, dst=None, custom_folder=None, postfn=None, watch=[], layers=[], ui_callback=None):
        self.hide = hide
        self.rect = Rect(rect)
        self.bg = normalize_color(bg)
        self.fmt = fmt
        self.prefix = prefix
        self.dst = Path(dst).expanduser().resolve() if dst else None
        self.custom_folder = custom_folder
        self.postfn = postfn
        self.ui_callback = ui_callback
        self.watch = [Path(w).expanduser().resolve() for w in watch]
        self.rasterizer = rasterizer
        self.self_rasterizing = False
        self.layers = layers
        if not rasterizer:
            if self.fmt == "svg":
                self.rasterizer = "svg"
            else:
                system = platform.system()
                if system == "Darwin":
                    self.rasterizer = "drawbot"
                else:
                    self.rasterizer = "cairo"
    
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

    async def run(self, render_pass):
        if inspect.iscoroutinefunction(render_pass.fn):
            return await render_pass.fn(*render_pass.args)
        else:
            return render_pass.fn(*render_pass.args)
    
    async def runpost(self, result, render_pass):
        if self.postfn:
            return self.postfn(self, result)
        else:
            return result
        
    def send_preview(self, previewer, result, render_pass):
        previewer.send(SVGPen.Composite(result, self.rect, viewBox=True), bg=self.bg, max_width=800)


class drawbot_script(renderable):
    def __init__(self, rect=(1080, 1080), scale=1, svg_preview=0, **kwargs):
        if not db:
            raise Exception("DrawBot not installed!")
        super().__init__(rect=Rect(rect).scale(scale), **kwargs)
        self.svg_preview = svg_preview
        self.self_rasterizing = True
    
    async def run(self, render_pass):
        use_pool = True
        if use_pool:
            pool = AppKit.NSAutoreleasePool.alloc().init()
        try:
            db.newDrawing()
            db.size(self.rect.w, self.rect.h)
            render_pass.fn(*render_pass.args)
            result = None
            if render_pass.action in [Action.RenderAll] or not self.svg_preview:
                render_pass.output_path.parent.mkdir(exist_ok=True, parents=True)
                db.saveImage(str(render_pass.output_path))
                result = render_pass.output_path
            else:
                with tempfile.NamedTemporaryFile(suffix=".svg") as tf:
                    db.saveImage(tf.name)
                    result = tf.read().decode("utf-8")
            db.endDrawing()
        finally:
            if use_pool:
                del pool
        return result
    
    def send_preview(self, previewer, result, render_pass):
        if self.svg_preview:
            previewer.send(f"<div class='drawbot-render'>{result}</div>", bg=self.bg, max_width=800)
        else:
            r = self.rect
            previewer.send(str(render_pass.output_path), Rect(0, 0, r.w/2, r.h/2), bg=self.bg, image=True)


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
            self.timeline = None
    
    def folder(self, filepath):
        return filepath.stem # TODO necessary?
    
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
                    frames = list(self.timeline.workareas[0])
                except:
                    frames = self.all_frames()
                #if hasattr(self.timeline, "find_workarea"):
                #    frames = self.timeline.find_workarea()
        return frames
    
    def passes(self, action, layers, indices=[]):
        frames = self.active_frames(action, layers, indices)
        return [RenderPass(self, "{:04d}".format(i), [Frame(i, self, layers)]) for i in frames]


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