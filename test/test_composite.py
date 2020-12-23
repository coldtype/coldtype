from coldtype.test import *

cheee = Font.Cacheable("~/Type/fonts/fonts/Eckmannpsych-Variable.ttf")

@animation(timeline=Timeline(120), bg=0)
def simple(f):
    e = f.a.progress(f.i, easefn="qeio", loops=1).e
    le = f.a.progress(f.i, easefn="linear", loops=3, cyclic=0).e
    return DATPenSet([
        #DATPen().rect(f.a.r).f(0, 0.25),
        (StyledString("WHOA",
            Style(mutator, 250, wdth=1-e, wght=e, ro=1))
            .pen()
            .align(f.a.r)
            .rotate(360*le)
            .f(1)
            .f(hsl(le, s=1))
            .s(0).sw(5))])#.blendmode(skia.BlendMode.kLighten)

@animation((1200, 500), timeline=Timeline(60), bg=1, composites=1, solo=1)
def interpolation(f):
    e = f.a.progress(f.i, easefn="qeio", loops=1).e
    return DATPenSet([
        #DATPen().rect(f.a.r).f(1),
        interpolation.last_result,
        (StyledString("Y",
            Style(cheee, 500, yest=1-e*0.5, grvt=e, opsz=1-e, ro=1))
            .pen()
            .align(f.a.r, x="mnx")
            .translate(30+820*e, 20*e)
            .rotate(180*e)
            .f(1)
            .s(0).sw(8))
            ]).color_phototype(f.a.r, blur=3, cut=110, cutw=15)