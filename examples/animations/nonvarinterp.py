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
    i = "{:.7f}".format(f.e("eeio", 1))
    ro = -360*f.e("l", 3, cyclic=0)

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
            .f(hsl(0.4, 1, 0.3))
            .mod_contour(18, lambda p:p.rotate(ro))
            #.mod_contour(4, lambda p:p.rotate(ro))
            .removeOverlap()
            .tag("Interpolation")
            .ch(b3d("Text", lambda bp: bp
                .extrude(f.e("eeio", 1, rng=(0.01, 3))))))])

def build(_):
    #print(__FILE__)
    # write render cmd to blender.txt
    # watch.py then takes care of calling the actual render
    # monitor for files as they come in?
    # monitor for crash file?
    #pass
    cb = Path("~/.coldtype/blender.txt").expanduser()
    if cb.exists():
        cb.unlink()
    cb.write_text(f"render,{str(__FILE__)}")