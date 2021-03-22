from coldtype import *
from drafting.drawbot import dbdraw, dbdraw_with_filters

co = Font("assets/ColdtypeObviously.designspace")
tl = Timeline(50, storyboard=[0])

@drawbot_animation(rect=(900, 500), bg=0.5, timeline=tl)
def db_script_test(f):
    e = f.a.progress(f.i, loops=1, easefn="eeio").e
    (StyledString("COLDTYPE",
        Style(co, 150, tu=100+-730*e, ro=1, r=1))
        .pens()
        .align(f.a.r)
        .rotate(15*(1-e))
        .skew(e*0.75)
        .f(hsl(e, s=1, l=1-e*0.35))
        .understroke(sw=20)
        .scale(1-1*e*0.5)
        .chain(dbdraw_with_filters(f.a.r, [["pixellate", dict(scale=5.0+5.0*e)]])))