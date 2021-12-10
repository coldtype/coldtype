from coldtype.test import *
from coldtype.fx.skia import fill, phototype

@animation((540, 540), timeline=Timeline(120), bg=0, solo=0, composites=1)
def simple(f):
    return DATPens([
        f.last_render(),
        (StSt("WHOA", mutator, 100
            , wdth=f.e("qeio", r=(1, 0))
            , wght=f.e("qeio")
            , ro=1)
            .align(f.a.r)
            .rotate(f.e("l", 3, cyclic=0, r=(0, 360)))
            .f(hsl(f.e("l", 3, cyclic=0), s=1))
            .s(0)
            .sw(2))])

@animation((1200, 800), timeline=90, bg=1, composites=1)
def interpolation(f):
    return (PS([
        f.last_render(lambda p: p.translate(2, -2).ch(fill(1))),
        (StSt("C", co, 500-f.e("qeio", 1)*300, wdth=1, ro=1, tu=0)
            .align(f.a.r, x="mnx")
            .translate(30+790*f.e("ceio", 1), 100)
            .f(0).s(1).sw(10))])
        | phototype(f.a.r, fill=0, blur=3, cut=130, cutw=25))

def release(passes):
    (FFMPEGExport(interpolation, passes, loops=4)
        .h264()
        .write()
        .open())