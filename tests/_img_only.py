from coldtype import *

@animation((540, 540), bg=None)
def scratch(f):
    res = (StSt("ASDF", Font.MuSan(), 150, wght=f.e("eeio", 1), wdth=0)
        .align(f.a.r)
        .f(0)
        .insert(0, lambda p: P(p.ambit(ty=1).inset(-20))
            .fssw(-1, 0, 1)
            .attr(dash=[5, 2])))
    
    return res