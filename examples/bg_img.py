from coldtype import *
from coldtype.fx.skia import phototype
from coldtype.img.skiaimage import SkiaImage

r = Rect(1080, 540)

@renderable(r, render_only=1)
def bg_maker(r):
    print(bg_maker.pass_path(0))
    return P(
        P(r).f(Gradient.Vertical(r, hsl(0.3), hsl(0.6))),
        StSt("BG", Font.MuSan(), 250, wght=1, wdth=0)
            .f(1)
            .align(r)
            .ch(phototype(r, blur=3, cutw=30)))

@renderable(r, bg=lambda: SkiaImage("examples/renders/bg_img_bg_maker.png"))
def bg_user(r):
   return P(r.inset(50)).fssw(-1, 1, 6)