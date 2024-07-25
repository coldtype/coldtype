from coldtype import *
from coldtype.img.skiaimage import SkiaImage
from coldtype.timing.timeline import Timeline

from shutil import copy

images = list(sorted(Path(__inputs__[0]).glob("*.jpg"), key=lambda p: p.name))
img = SkiaImage(images[0])

class passthrough(animation):
    def __init__(self, images, fps, looping=False, **kwargs):
        self.images = images
        self.looping = looping

        if self.looping:
            timeline = Timeline(len(images)*2-2, fps)
        else:
            timeline = Timeline(len(images), fps)
        
        img = SkiaImage(images[0])
        super().__init__(img.rect(), timeline, fmt=images[0].suffix[1:], **kwargs)
        self.self_rasterizing = True
    
    def normalize_result(self, pens):
        return pens
    
    def run(self, render_pass, renderer_state):
        idx = render_pass.idx
        if self.looping:
            t = idx/self.timeline.duration
            idx = round(ez(t, "l", 1, rng=(0, len(self.images)-1)))
        
        result = None
        if renderer_state and renderer_state.previewing:
            return images[idx]
        else:
            render_pass.output_path.parent.mkdir(exist_ok=True, parents=True)
            copy(images[idx], render_pass.output_path)
            result = render_pass.output_path
        return result

@passthrough(images, 24, looping=True)
def viewer(_): return None

def release(_):
    FFMPEGExport(viewer, loops=2).prores().write(True)