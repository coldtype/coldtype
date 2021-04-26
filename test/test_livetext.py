#coldtype -wt -wp C -hkb

from coldtype.test import *
from drafting.text.richtext import RichText

@renderable((1200, 500), rstate=1)
def stub(r, rs):
    txt = rs.read_text(clear=False)
    
    rt = (RichText(r,
        ("This is a\n" + (txt + "\n" if txt else "") + "program").upper(),
        dict(default=Style(mutator, 100, wght=0.5, wdth=0.15)),
        fit=r.w - 100 if txt else None)
        .xa()
        .align(r)
        .f(0))
    
    return DATPens([
        DATPen().rect(r.inset(20)).f(0, 0.5).s(0).sw(5),
        rt.pen().f(0).translate(5, -5),
        rt.f(1)
        ])
