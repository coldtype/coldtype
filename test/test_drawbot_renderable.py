from coldtype import *
from drawBot import *

co = Font("assets/ColdtypeObviously.designspace")

PREVIEW_WITH_SVG = 0

long_txt = """This code is a mix of DrawBot and Coldtype, meant to demonstrate that Coldtype primitives (like designspace-reading) can be combined with DrawBot primitives like multi-line text support and the Mac Font library."""

@drawbot_script(rect=(900, 500), scale=1, svg_preview=PREVIEW_WITH_SVG, bg=0)
def db_script_test(r):
    ri = r.inset(20, 20)

    fill(*hsl(0.5))
    oval(*ri.take(0.5, "mxx").square())

    if not PREVIEW_WITH_SVG: # Doesn't work with SVG output (internal drawBot issue)
        im = ImageObject()
        with im:
            size(500, 500)
            image("https://static.goodhertz.co/statics/store/img/logos/hertz-color-danico-250-lssy.png", (0, 0))
            im.photoEffectMono()
        
        x, y = im.offset()
        image(im, (250+x, -10+y))

    fontSize(19)
    font("Georgia-Italic")
    fill(*hsl(0.9, s=0.7, l=0.6))
    textBox(long_txt, ri.take(200, "mny").take(250, "mnx"))

    (StyledString("COLDTYPE",
        Style(co, 150, ro=1))
        .pen()
        .align(ri, "mnx", "mxy")
        .f(Gradient.Horizontal(ri,
            hsl(0.05, s=0.7, l=0.6),
            hsl(0.15, s=0.7, l=0.6)))
        .s(0)
        .sw(3)
        .db_drawPath())

    saveImage("test/drawbot/saved_from_drawbot_test.pdf")