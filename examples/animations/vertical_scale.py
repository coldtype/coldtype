from coldtype import *

@animation(tl=50, bg=1)
def scratch(f):
    ri = f.a.r.inset(30)
    rng = (1, 3)
    fs = 170

    hello = (StSt("Hello", Font.MuSan(), fs, case="upper", wght=1, wdth=1, fit=ri.w)
        .align(ri, "N", tv=1, tx=0)
        .map(lambda i, p: p.scale(1, f.adj(i).e("eeio", rng=rng), pt=p.ambit(tv=1).pn)))
    
    there = (StSt("There", Font.MuSan(), fs+100, case="upper", wght=0.5, wdth=1, fit=ri.w)
        .align(ri, "C", tv=1, tx=0)
        .map(lambda i, p: p.scale(1, f.adj(i).e("eeio", rng=(3, 0.65)), pt=p.ambit(tv=1).pc)))

    world = (StSt("World", Font.MuSan(), fs, case="upper", wght=1, wdth=1, fit=ri.w)
        .align(ri, "S", tv=1, tx=0)
        .map(lambda i, p: p.scale(1, f.adj(i).e("eeio", rng=rng), pt=p.ambit(tv=1).ps)))
    
    return hello + there + world