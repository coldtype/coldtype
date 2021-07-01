from coldtype import *
from shutil import copy2


class logo(renderable):
    def __init__(self, **kwargs):
        super().__init__(rect=(500, 150), fmt="svg", rasterizer="svg", viewBox=False, **kwargs)
    
    def package(self):
        src = self.output_folder / f"{self.filepath.stem}_{self.name}.svg"
        dst = "docs/_static/coldtype_logo.svg"
        copy2(src, dst)


@logo()
def coldtype(r):
    return (StSt("COLDTYPE", "assets/ColdtypeObviously-VF.ttf",
            170, wdth=0.25, rotate=10, r=0)
        .f(1)
        .track_to_rect(r.inset(20), pullToEdges=0)
        .align(r))