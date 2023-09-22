from coldtype import *
from coldtype.runon import RunonEnumerable
from coldtype.drawbot import tobp # mac-only

# inspired by https://gist.github.com/connordavenport/12cc057798b175782431a883e63386db

@animation((1080, 540), bg=0, tl=60)
def bitmap_font(f):
    txt = (StSt("COLD\nTYPE", Font.ColdtypeObviously(), 250
        , wdth=f.e("eeio")
        , tu=f.e("eeio", rng=(50, 350))
        , leading=30)
        .align(f.a.r)
        .pen()
        .chain(tobp))

    def enumerator(x:RunonEnumerable):
        if txt.pointInside(x.el.r.pc):
            return P().rect(x.el.r.inset(1))
    
    return P().enumerate(f.a.r.grid(50, 25), enumerator).f(1)