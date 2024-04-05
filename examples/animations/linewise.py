from coldtype import *

@animation((1080, 540), tl=60)
def scratch1(f):
    return (Glyphwise("COLD\nTYPE", lambda x:
        Style(Font.ColdObvi(), 200
            , wdth=f.adj(x.l*7).e("eeio")))
        .lead(10)
        .xalign(f.a.r)
        .align(f.a.r))

@animation((1080, 540), tl=60)
def scratch2(f):
    txt = "COLD\nTYPE"
    return (P().enumerate(txt.splitlines(), lambda x:
        StSt(x.el, Font.ColdObvi(), 200
            , wdth=f.adj(x.i*7).e("eeio")))
        .stack(10)
        .xalign(f.a.r)
        .align(f.a.r))
