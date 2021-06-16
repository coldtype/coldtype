from coldtype.blender import *

fnt = Font.Cacheable("~/Type/fonts/fonts/OhnoFatfaceVariable.ttf")

@b3d_renderable()
def draw_bg(r):
    return DATPens([
        (DATPen(r.inset(0, 0)).f(hsl(0.37, 1, 0.3))
            .tag("BG2")
            .chain(b3d("Text", plane=1)))])

@b3d_animation(timeline=30, layer=1)
def draw_txt(f):
    return DATPens([
        (StSt("Wavey", fnt, 300,
            wdth=f.e(1, rng=(0.25, 1)),
            opsz=f.e(1))
            .pen()
            .align(f.a.r)
            .f(hsl(0.7, 1))
            .tag("Wavey")
            .chain(b3d("Text",
                extrude=f.e(1, rng=(0.05, 3)))))])