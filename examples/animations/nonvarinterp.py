from coldtype import *
from coldtype.blender import *

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")
mdpb = Font.Cacheable("≈/MDNichrome0.7-Black.otf")
mdpl = Font.Cacheable("≈/MDNichrome0.7-Light.otf")
mdiob = Font.Cacheable("≈/MDIO0.2-Bold.otf")
mdior = Font.Cacheable("≈/MDIO0.2-Regular.otf")

r = Rect(1080, 1080)

def build(font, **kwargs):
    return (StSt("Inter-\npolation",
        font, 250, leading=50, **kwargs)
        .align(r.take(0.85, "mxy"))
        .pen())

a = build(mdpl)
b = build(mdpb)

@b3d_animation(r, timeline=Timeline(90))
def nonvarinterp(f):
    i = "{:.2f}".format(f.e("eeio", 1))

    return DPS([
        (StSt(i, mdiob, 150)
            .align(f.a.r.take(0.4, "mny"))
            .pen()
            .f(1)
            .tag("Num")
            .ch(b3d("Text", lambda bp:
                bp.extrude(0.5)))),
        (a.interpolate(f.e("eeio", 1), b)
            .f(hsl(0.4, 1, 0.3))
            .mod_contour(18, lambda p:
                p.rotate(-360*f.e("l", 5, cyclic=0)))
            .tag("Interpolation")
            .ch(b3d("Text", lambda bp:
                bp.extrude(f.e("eeio", 1, rng=(0.1, 2))))))])