from coldtype import *
from coldtype.blender import *

mdpb = Font.Find("MDNichrome0.7-Black")
mdpl = Font.Find("MDNichrome0.7-Light")
mdiob = Font.Find("MDIO0.2-Bold")
mdior = Font.Find("MDIO0.2-Regular")

r = Rect(1080, 1080)

def build(font, **kwargs):
    return (StSt("Inter-\npolation",
        font, 250, leading=50, **kwargs)
        .xalign(r)
        .align(r.take(0.85, "mxy"))
        .pen())

a = build(mdpl)
b = build(mdpb)

@b3d_animation(r, timeline=Timeline(90))
def nonvarinterp(f):
    i = "{:.7f}".format(f.e("eeio", 1))

    return DPS([
        (StSt(i, mdiob, 72)
            .align(f.a.r.take(0.4, "mny"), th=0)
            .pen()
            .f(hsl(0.65, 1, 0.3))
            .tag("Num")
            .ch(b3d("Text", lambda bp: bp
                .extrude(f.e(1, rng=(0.01, 0.5)))
                .emission(hsl(0.65, 1, 0.3), 1)))),
        (a.interpolate(f.e("eeio", 1), b)
            .mod_contour(18, lambda p: p
                .rotate(f.e("l", 3, cyclic=0, rng=(0, -360))))
            .f(hsl(0.4, 1, 0.3))
            .removeOverlap()
            .tag("Interpolation")
            .ch(b3d("Text", lambda bp: bp
                .extrude(f.e("eeio", 1, rng=(0.01, 3))))))])