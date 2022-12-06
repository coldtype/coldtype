from coldtype import *
from coldtype.fx.warping import warp
from coldtype.fx.skia import phototype

logos = raw_ufo("assets/logos.ufo")

@renderable((1200, 600))
def nameplate(r, fontSize=500, wdth=0.25, rotate=0):
    return (P(
        P(r).f(0),
        StSt("COLDTYPE", Font.ColdObvi(), fontSize
            , wdth=wdth
            , rotate=rotate
            , tu=-50, r=1)
            .fssw(1, 0, 20, 1)
            .align(r)
            .ch(phototype(r, cutw=10)),
        P().glyph(logos["goodhertz_logo_2019"])
            .scale(0.5)
            .align(r)
            .f(1)
            .ch(warp(5, mult=90))
            .ch(phototype(r, blur=8, fill=hsl(0.61, 0.7, 0.6)))
            .blendmode(BlendMode.Multiply)))

@renderable()
def square(r):
    hr = r.take(0.3333, "mny").round()
    return (nameplate.func(hr, 350, 0.5, 20)
        + nameplate.func(hr, 350, 0.4, 10).translate(0, hr.h)
        + nameplate.func(hr, 350, 0.25, 0).translate(0, hr.h*2))