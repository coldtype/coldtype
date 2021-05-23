from coldtype.test import *

@animation((1000, 500), timeline=Timeline(120), bg=0, solo=0, composites=1)
def simple(f):
    e = f.a.progress(f.i, easefn="qeio", loops=1).e
    le = f.a.progress(f.i, easefn="linear", loops=3, cyclic=0).e
    return DATPens([
        f.last_render(),
        #DP(f.a.r).f(hsl(0.9)),
        (StSt("WHOA", mutator, 100, f.a.r, wdth=1-e, wght=e, ro=1)
            .align(f.a.r)
            .rotate(360*le)
            .f(hsl(le, s=1))
            .s(0)
            .sw(2))])

@animation((1200, 800), timeline=Timeline(90, fps=30, jumps=[int(90/4)]), bg=1, composites=1, solo=1)
def interpolation(f):
    e = f.a.progress(f.i, easefn="qeio", loops=1).e

    return (DATPens([
        f.last_render(lambda p: p.translate(2, -2)),
        (StyledString("C",
            Style(co, 500-e*300, wdth=1, ro=1, tu=0))
            .pen()
            #.mod_contour(0, lambda p: p.rotate(-360*le))
            .align(f.a.r, x="mnx")
            .translate(30+790*e, 100)
            #.rotate()
            .f(0)
            .s(1).sw(10))
            ])
        .phototype(f.a.r, fill=0, cut=110, cutw=15)
        -.color_phototype(f.a.r, blur=5, cut=115, cutw=15))

def release(passes):
    (FFMPEGExport(interpolation, passes, loops=4)
        .h264()
        .write()
        .open())