from coldtype import *

mdpb = Font.Cacheable("~/Type/fonts/fonts/MDNichrome0.7-Black.otf")
mdpl = Font.Cacheable("~/Type/fonts/fonts/MDNichrome0.7-Light.otf")

r = Rect(1920, 1080)

def build(font, **kwargs):
    return (StSt("Inter-\npolation",
        font, 450, leading=50, **kwargs)
        .align(r)
        .pen())

a = build(mdpb)
b = build(mdpl)

@animation(r, timeline=Timeline(120))
def nonvarinterp(f):
    return (a.interpolate(f.e("eeio", 2), b).f(None).s(hsl(0.9, 1)).sw(5)
        .mod_contour(8, lambda p:
            p.rotate(-360*f.e("l", 7, 0))))