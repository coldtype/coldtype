from coldtype import *
from coldtype.fx.warping import warp
from coldtype.text.richtext import PythonCode

### Code that displays itself

styles = ["R", "Bl", "B.*I"]
vulfs = [Font.Find(f"Mono{s}", "vulf") for s in styles]
defaults = [vulfs[0], hsl(0.65, 0.6, 0.65)]
lookup = PythonCode.DefaultStyles(*vulfs)
rnds1 = random_series()

@aframe(bg=0)
def code1(f):
    def render_code(txt, styles):
        style = styles[0] if len(styles) > 0 else "default"
        font, fill = lookup.get(style, defaults)
        return txt, Style(font, 22, fill=fill)

    ri = f.a.r.inset(20)
    
    return (PythonCode(ri
        , Path(__FILE__).read_text()[:]
        , render_code
        , leading=8)
        .align(ri, "W")
        .removeSpacers()
        .collapse()
        .pmap(lambda i, p: p.rotate(-15+rnds1[i]*30))
        .pmap(warp(2, 0, 0, mult=30)))