from coldtype import *
from coldtype.fx.skia import phototype
from coldtype.img.skiaimage import SkiaImage

@animation((540, 540), tl=Timeline(30, 18), render_only=1)
def bg_maker(f):
    return P(
        P(f.a.r).f(hsl(f.e("l", 0))),
        StSt(f"{f.i}", Font.JBMono(), 250, wght=1, wdth=0)
           .f(1)
           .align(f.a.r, tx=0))

@animation(bg_maker.rect, bg=lambda _,rp: SkiaImage(bg_maker.pass_path(rp.idx)).rotate(31), render_bg=1)
def bg_user(f):
  return P(f.a.r.inset(40)).fssw(-1, 1, 6)