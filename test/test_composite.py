from coldtype.test import *

@animation((1000, 500), timeline=Timeline(120), bg=0)
def simple(f):
    e = f.a.progress(f.i, easefn="qeio", loops=1).e
    le = f.a.progress(f.i, easefn="linear", loops=3, cyclic=0).e
    return DATPens([
        #DATPen().rect(f.a.r).f(0, 0.25),
        (StyledString("WHOA",
            Style(mutator, 250, wdth=1-e, wght=e, ro=1))
            .pen()
            .align(f.a.r)
            .rotate(360*le)
            .f(1)
            .f(hsl(le, s=1))
            .s(0).sw(5))]).blendmode(skia.BlendMode.kDifference)

@animation((1200, 800), timeline=Timeline(90, fps=30, jumps=[int(90/4)]), bg=1, composites=1, solo=1)
def interpolation(f):
    e = f.a.progress(f.i, easefn="qeio", loops=1).e
    #le = f.a.progress(f.i, easefn="qeio", loops=2, cyclic=True).e

    return (DATPens([
        DATPen().rect(f.a.r).f(1),
        interpolation.last_result.copy().translate(2, -2) if interpolation.last_result else None,
        (StyledString("C",
            Style(co, 500-e*300, wdth=1, ro=1, tu=0))
            .pen()
            #.mod_contour(0, lambda p: p.rotate(-360*le))
            .align(f.a.r, x="mnx")
            .translate(30+790*e, 100)
            #.rotate()
            .f(1)
            .s(0).sw(10))
            ])
        .color_phototype(f.a.r, blur=5, cut=135, cutw=15))

def release(passes):
    (FFMPEGExport(interpolation, passes, loops=4)
        .h264()
        .write()
        .open())