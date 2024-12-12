from coldtype import *
from coldtype.img.skiaimage import SkiaImage
from coldtype.fx.skia import precompose, temptone

@renderable((540, 540/2), bg=hsl(0.3), render_only=0)
def test_image(r):
    return StSt("HELLO", Font.MuSan(), 100, wght=1).align(r, ty=1).f(hsl(0.9, 0.6, 0.6))

@animation((1080, 1080), tl=36)
def rotate(f):
    src = test_image.render_to_disk(render_bg=1)[0]
    return (SkiaImage(src)
        .resize(1)
        .align(f.a.r)
        .rotate(45-f.i*10)
        #.in_pen().fssw(bw(0, 0.1), 0, 1)
        .ch(precompose(f.a.r))
        .ch(temptone(-0.20, 0.70)))

@animation((540, 540))
def resize(f):
    return (SkiaImage(test_image.pass_path(0))
        .resize(0.85)
        .align(f.a.r, "NE"))
