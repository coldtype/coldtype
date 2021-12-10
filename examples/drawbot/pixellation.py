from coldtype import *
from coldtype.drawbot import *

@drawbot_animation((1080, 540), bg=0.8, timeline=50)
def db_script_test(f):
    e = f.e()
    (StSt("COLDTYPE", Font.ColdObvi(), 150, tu=100+-730*e, ro=1, r=1)
        .align(f.a.r)
        .rotate(15*(1-e))
        .skew(e*0.75)
        .f(hsl(e, s=1, l=1-e*0.35))
        .understroke(sw=20)
        .scale(1-1*e*0.5)
        .chain(dbdraw_with_filters(f.a.r,
            [["pixellate", dict(scale=5.0+5.0*e)]])))