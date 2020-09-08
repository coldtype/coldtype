from coldtype import *
from drawBot import *


co = Font("assets/ColdtypeObviously.designspace")
tl = Timeline(50, storyboard=[0, 15, 29])


@drawbot_animation(rect=(900, 500), svg_preview=0, bg=0, timeline=tl)
def db_script_test(f):
    a:Animation
    r = f.a.r
    ri = r.inset(20, 20)

    e = f.a.progress(f.i, loops=1, easefn="eeio").e

    im = ImageObject()
    with im:
        size(*r.wh())
        fill(*hsl(0.9, s=1, l=0.6))
        drawPath(StyledString("COLDTYPE", Style(co, 150, tu=100-500*e)).pen().align(r).rotate(15*(1-e)).translate(0, 10).bp())
        im.gaussianBlur(radius=max(0.0001, 50*e))
    
    x, y = im.offset()
    image(im, (x, y))