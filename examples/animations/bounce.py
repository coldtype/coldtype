from coldtype import *

@animation(tl=60, bg=1)
def scratch(f):
    ri = f.a.r.inset(50)
    
    a = (StSt("COLD", Font.ColdObvi(), 130, wght=1, wdth=1, fit=ri.w-10, tu=500, tl=500)).scaleToWidth(ri.w).align(ri, "S").skew(-1, 0)
    
    b = (StSt("COLD", Font.ColdObvi(), 470, wght=1, wdth=0.5, fit=ri.w-10)).scaleToWidth(ri.w).align(ri, "N")

    def interp(x):
        e = f.adj(x.i*-2).e("eeo", 1)
        return (x.el.copy()
            .interpolate(e, b[x.i].copy()))

    return P().enumerate(a, interp).f(0)