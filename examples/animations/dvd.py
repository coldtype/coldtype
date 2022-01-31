from coldtype import *

dvdr = Rect(500, 250)

font = "OhnoFatfaceV"
speed = 5
initial = dict(x=250, y=250, c=0, xs=speed, ys=speed)

@animation(tl=Timeline(300, 48), memory=initial, bg=0)
def scratch(f, m):
    r = f.a.r.inset(10)

    m.x += m.xs
    m.y += m.ys

    if m.x <= r.x or (r.x + m.x + dvdr.w) >= f.a.r.mxx:
        m.xs = -m.xs
        m.c += random()*0.35

    if m.y <= r.y or (r.y + m.y + dvdr.h >= f.a.r.mxy):
        m.ys = -m.ys
        m.c += random()*0.35
    
    a, b = (r.drop(dvdr.w, "E")
        .drop(dvdr.h, "N")
        .ipos(Point(m.x, m.y)))
    
    c = hsl(m.c, 0.8, 0.7)
    return P(
        P(dvdr).t(m.x, m.y).fssw(-1, c, 10),
        (StSt("Aa", font, 220
            , opsz=b, wdth=a)
            .f(c)
            .align(dvdr.offset(m.x, m.y)))) 