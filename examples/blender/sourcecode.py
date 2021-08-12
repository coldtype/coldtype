from coldtype import *
from coldtype.blender import *
from coldtype.text.richtext import PythonCode
from noise import pnoise3


def vulf(suffix):
    return Font.Find(f"VulfMono{suffix}.otf")

vulfs = [vulf(s) for s in
    ["Regular", "Bold", "BoldItalic"]]


defaults = [vulfs[0], hsl(0.65, 0.6, 0.35)]
lookup = PythonCode.DefaultStyles(*vulfs)


@b3d_animation(bg=0)
def code(f):
    
    def render_code(txt, styles):
        if len(styles) > 0:
            style = styles[0]
        else:
            style = "default"
        font, fill = lookup.get(style, defaults)
        return txt, Style(font, 22, fill=fill)
    
    def terrain(p):
        x, y = p.ambit().xy()
        pn = pnoise3(x*0.005, y*0.005, 0)
        p.ch(b3d(lambda bp: bp
            .extrude(0.05+0.85*(1+pn))))
    
    return (PythonCode(f.a.r.inset(20),
        code.filepath.read_text(),
        render_code, leading=10)
        .remove_blanklines()
        .remove_blanks()
        .collapse()
        .pmap(terrain))