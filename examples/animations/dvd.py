from coldtype import *

logo = P().rect(Rect(450, 250))
dvdr = (logo.ambit())

@animation(tl=Timeline(300, 48)
    , memory=dict(x=250, y=250, c=0, xs=5, ys=5)
    , bg=0)
def scratch(f, m):
    r = f.a.r.inset(0)

    m.x += m.xs
    m.y += m.ys

    if m.x <= r.x or (r.x + m.x + dvdr.w) >= f.a.r.mxx:
        m.xs = -m.xs
        m.c += 0.15 + random()*0.35
    
    if m.y <= r.y or (r.y + m.y + dvdr.h >= f.a.r.mxy):
        m.ys = -m.ys
        m.c += 0.15 + random()*0.35
    
    a, b = (r.drop(dvdr.w, "E")
        .drop(dvdr.h, "N")
        .ipos(Point(m.x, m.y)))
    
    c = hsl(m.c, 0.8, 0.6)
    return P(
        logo.copy().t(m.x, m.y).fssw(-1, c, 2),
        (StSt("DVD", "OhnoFatfaceV", 170
            , opsz=a, wdth=b))
            .f(c)
            .align(dvdr.offset(m.x, m.y)))