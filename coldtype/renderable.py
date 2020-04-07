import inspect

from coldtype.geometry import Rect
from coldtype.color import normalize_color


class RenderPass():
    def __init__(self, fn, suffix, args):
        self.fn = fn
        self.args = args
        self.suffix = suffix
    
    async def run(self):
        if inspect.iscoroutinefunction(self.fn):
            return self.suffix, await self.fn(*self.args)
        else:
            return self.suffix, self.fn(*self.args)


class renderable():
    def __init__(self, rect=(1080, 1080), bg=0.1):
        self.rect = Rect(rect)
        self.bg = normalize_color(bg)
    
    def __call__(self, func):
        self.func = func
        return self
    
    def folder(self):
        return ""
    
    def passes(self, mode):
        return [RenderPass(self.func, "", [self.rect])]


class icon(renderable):
    valid_sizes = [16, 32, 64, 128, 256, 512, 1024]

    def __init__(self, sizes=[128, 1024], **kwargs):
        self.sizes = sizes
        super().__init__(**kwargs)
    
    def folder(self):
        return f"{self.func.__name__}_source"
    
    def passes(self, mode):
        sizes = self.sizes
        if mode == "render_all":
            sizes = self.valid_sizes
        return [RenderPass(self.func, str(size), [self.rect, size]) for size in sizes]