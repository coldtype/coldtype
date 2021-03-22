from coldtype import *
from shutil import copy2


class logo(renderable):
    def __init__(self, **kwargs):
        super().__init__(rect=(500, 150), fmt="svg", rasterizer="svg", viewBox=False, **kwargs)
    
    def package(self, filepath, output_folder):
        src = output_folder / f"{filepath.stem}_{self.name}.svg"
        dst = "docs/_static/coldtype_logo.svg"
        copy2(src, dst)


@logo()
def coldtype(r):
    return (StyledString("COLDTYPE",
        Style("assets/ColdtypeObviously-VF.ttf",
            170, wdth=0.25, rotate=10, r=0))
        .pens()
        .f(1)
        .track_to_rect(r.inset(20), pullToEdges=0)
        .align(r))