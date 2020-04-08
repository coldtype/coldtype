import inspect
import platform
from subprocess import run
from pathlib import Path

from coldtype.geometry import Rect
from coldtype.color import normalize_color
from coldtype.animation import Timeable, Frame
from coldtype.animation.timeline import Timeline


class RenderPass():
    def __init__(self, fn, suffix, args):
        self.fn = fn
        self.args = args
        self.suffix = suffix
        self.path = None
    
    async def run(self):
        if inspect.iscoroutinefunction(self.fn):
            return await self.fn(*self.args)
        else:
            return self.fn(*self.args)


class renderable():
    def __init__(self, rect=(1080, 1080), bg="whitesmoke", hide=False, fmt="png", rasterizer=None, prefix=None, dst=None, custom_folder=None):
        self.hide = hide
        self.rect = Rect(rect)
        self.bg = normalize_color(bg)
        self.fmt = fmt
        self.prefix = prefix
        self.dst = Path(dst).expanduser().resolve() if dst else None
        self.custom_folder = custom_folder
        self.rasterizer = rasterizer
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
    
    def passes(self, mode):
        return [RenderPass(self.func, self.func.__name__, [self.rect])]

    def package(self, filepath, output_folder):
        pass


class svgicon(renderable):
    def __init__(self, **kwargs):
        super().__init__(fmt="svg", **kwargs)
    
    def folder(self, filepath):
        return filepath.stem


class iconset(renderable):
    valid_sizes = [16, 32, 64, 128, 256, 512, 1024]

    def __init__(self, sizes=[128, 1024], **kwargs):
        super().__init__(**kwargs)
        self.sizes = sizes
    
    def folder(self, filepath):
        return f"{filepath.stem}_source"
    
    def passes(self, mode):
        sizes = self.sizes
        if mode == "render_all":
            sizes = self.valid_sizes
        return [RenderPass(self.func, str(size), [self.rect, size]) for size in sizes]
    
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
        self.duration = duration
        self.storyboard = storyboard
        if timeline:
            self.timeline = timeline
            self.t = timeline
            self.start = timeline.start
            self.end = timeline.end
            self.duration = timeline.duration
            self.storyboard = timeline.storyboard
    
    def folder(self, filepath):
        return filepath.stem # TODO necessary?
    
    def passes(self, mode):
        frames = self.storyboard
        if mode == "render_all":
            frames = list(range(0, self.duration))
        return [RenderPass(self.func, "{:04d}".format(i), [Frame(i, self)]) for i in frames]