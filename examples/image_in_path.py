from coldtype import *
from coldtype.raster import *

@renderable(bg=0)
def image(r):    
    shape = P().oval(r.inset(100)).align(r, ty=1)
    pts = shape.flatten(3).point_list(random_seed=0)

    return (P()
        .m(pts[0])
        .enumerate(pts[1:], lambda x: x.parent
            .l(x.el))
        .ep()
        .fssw(-1, 1, 1)
        .ch(phototype(r, 1, 170, 50)))

@renderable(bg=0, layer=0)
def in_path(r):
    return (StSt("COLD\nTYPE", Font.ColdObvi(), 340, wdth=1, fit=r.inset(200).w)
        .align(r, ty=1)
        .img(image.render_to_disk()[0], r, pattern=1)
        .f(0.1)
        .ch(luma(r, hsl(0.57, 1, 0.50))))