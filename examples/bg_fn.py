from coldtype import *

tl = Timeline(30, 12)

@animation((540, 540), tl=tl, render_only=1)
def bg_maker(f):
    return P(
        P(f.a.r).f(hsl(f.e("l", 0))),
        StSt(f"{f.i}", Font.JBMono(), 250, wght=1, wdth=0)
           .f(1)
           .align(f.a.r, tx=0))

@animation(bg_maker.rect, bg=lambda _,rp: bg_maker.pass_img(rp.idx).rotate(-rp.idx), render_bg=1, tl=tl)
def bg_user(f):
  return P(f.a.r.inset(40)).fssw(-1, 1, 6)