from coldtype import *
from coldtype.blender import *
from coldtype.fx.skia import rasterize

"""
Demonstration of how to display
an image on a plane in Blender
"""

img_path = __sibling__("media/rasterized_test.png")

img = (StSt("COLD\nTYPE", Font.ColdtypeObviously()
    , fontSize=500
    , wdth=0.25)
    .align(Rect(1080, 1080))
    .mapv(lambda p: p
        .f(Gradient.V(p.ambit(), hsl(0.3), hsl(0.7))))
    .ch(rasterize(Rect(1080, 1080), img_path)))

@b3d_renderable()
def show_img(r):
    return (P(r).f(-1).img(img_path, r)
        | b3d(lambda p: p, material="auto", plane=True))