from coldtype import *
from coldtype.img.skiaimage import SkiaImage

@renderable((540, 540/2), bg=hsl(0.3), render_only=1)
def test_image(r):
    return StSt("HELLO", Font.MuSan(), 100, wght=1).align(r, ty=1).f(hsl(0.9, 0.6, 0.6))

@animation()
def scratch(f):
    return (SkiaImage(test_image.pass_path(0))
        #.align(f.a.r)
        #.resize(4)
        #.t(-600, 0)
        .rotate(10)
        )
