from coldtype import *
from fontTools.ufoLib import UFOReader

logos = UFOReader("assets/logos.ufo").getGlyphSet()

@renderable((1200, 600), bg=0)
def nameplate(r, fontSize=500, wdth=0.25, rotate=0):
    return (P(
        StSt("COLDTYPE", Font.ColdObvi(), fontSize
            , wdth=wdth
            , rotate=rotate
            , tu=-50, r=1)
            .fssw(1, 0, 20, 1)
            .align(r),
        P().glyph(logos["goodhertz_logo_2019"])
            .scale(0.5)
            .align(r)
            .f(hsl(0.61, 0.7, 0.6))
            .blendmode(BlendMode.Multiply)))