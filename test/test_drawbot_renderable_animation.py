from coldtype import *

co = Font("assets/ColdtypeObviously.designspace")
tl = Timeline(50, storyboard=[0, 22])

@drawbot_animation(rect=(900, 500), svg_preview=0, bg=0.5, timeline=tl)
def db_script_test(f):
    e = f.a.progress(f.i, loops=1, easefn="eeio").e
    #DATPen().oval(f.a.r).db_drawPath(f.a.r, [
        #["gaussianBlur", {"radius":3+20*e}]
    #])

    (StyledString("COLDTYPE",
        Style(co, 150, tu=100+-730*e, ro=1, r=1))
        .pens()
        .align(f.a.r)
        .rotate(15*(1-e))
        .skew(e*0.5)
        .filmjitter(e, speed=(20, 30), scale=(3, 4))
        .f(hsl(e, s=1, l=1-e*0.35))
        .understroke(sw=20)
        .scale(1-1*e*0.5)
        .db_drawPath(f.a.r, [ # TODO autogenerate signatures to make these autocomplete-able?
            #["pixellate", dict(scale=15.0)],
            ["gaussianBlur", {"radius":3+20*e}],
        ]))