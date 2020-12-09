from coldtype import *
from coldtype.warping import warp_fn
from coldtype.animation.easing import ease
from coldtype.text.richtext import PythonCode

### Code that is
### it’s own animation
### (and is not very fast)

def vulf(suffix):
    return Font.Cacheable(
        f"~/Type/fonts/fonts/vulf/VulfMono{suffix}.otf")

vulfs = [vulf(s) for s in ["Regular", "Bold", "BoldItalic"]]
defaults = [vulfs[0], hsl(0.65, 0.6, 0.65)]
lookup = PythonCode.DefaultStyles(*vulfs)
rnds1 = random_series()

@animation(bg=0, timeline=Timeline(60), storyboard=[50])
def code1(f):
    e = f.a.progress(f.i).e*1.05

    def render_code(txt, styles):
        style = styles[0] if len(styles) > 0 else "default"
        font, fill = lookup.get(style, defaults)
        return txt, Style(font, 22, fill=fill)
    
    def rotate(i, p):
        ee = ease("eeo", min(1, max(0, (e-rnds1[i])*5)))
        p.rotate(ee[0]*(360 if i%2==0 else -360))
        return p

    ri = f.a.r.inset(20)
    rt = PythonCode(ri, Path(__FILE__).read_text()[:],
        render_code,
        graf_style=GrafStyle(leading=8))
    
    return (rt
        .align(ri, "mnx", "mxy", tv=1)
        .scale(1)
        .remove_blanklines()
        .collapse()
        .pmap(rotate)
        .pmap(lambda i, p:
            (p.flatten(2)
                .nlt(warp_fn(0, 0, mult=25)))))