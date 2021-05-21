from coldtype import *

mdpb = Font.Cacheable("~/Type/fonts/fonts/MDNichrome0.7-Black.otf")
mdpl = Font.Cacheable("~/Type/fonts/fonts/MDNichrome0.7-Light.otf")

r = Rect(1920, 1080)

def build(font, **kwargs):
    return (StSt("Inter-\npolation", font, 450, leading=50, **kwargs)
        .align(r)
        .pen())

a = build(mdpb)
b = build(mdpl)

@animation(r, timeline=Timeline(120))
def nonvarinterp(f):
    e = f.a.progress(f.i, loops=1, easefn="eeio").e
    e2 = f.a.progress(f.i, loops=5, cyclic=0, easefn="linear").e
    return (None)