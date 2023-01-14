from coldtype import *

at = AsciiTimeline(2, 30, """
                                        <
    a        a          b        b
""")

@animation((1080, 1080), tl=at, bg=1)
def scratch(f):
    a = (StSt(txt:="TEXT"
        , font:=Font.MuSan()
        , fs:=200
        , wght=0
        , wdth=1)
        .align(ri:=f.a.r.inset(110), "N"))

    b = (StSt(txt, font, fs-20, wght=1, wdth=1).align(ri, "S"))

    def interp(x):
        e = at.kf(keyframes=dict(a=0, b=1), offset=x.e*4)
        return (x.el.copy() 
            .interpolate(e, b[x.i].copy())
            .f(hsl(e, 0.9)))
    
    return P(a, b, P().enumerate(a, interp))