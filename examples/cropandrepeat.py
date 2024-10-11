from coldtype import *
from coldtype.fx.skia import phototype

@aframe(bg=hsl(0.93, 0.6, 0.5))
def scratch(f):
    def crop(e, p):
        _e = 10+ez(e, "eei") * p.ambit(tx=0, ty=1).h
        _crop = P(p.ambit(tx=0, ty=1)
            .take(_e, "N", forcePixel=1))
        return (p
            .intersection(_crop)
            .unframe()
            .align(f.a.r, "S", tx=1)
            .t(ez(e, "seio", 1)*470, 0))

    return (StSt("CROP AND REPEAT", Font.MuSan()
        , fontSize=170
        , wght=0
        , wdth=1
        , fit=f.a.r.w)
        .layer(47)
        .mape(crop)
        .stack(4)
        .scale(0.7)
        .align(f.a.r.drop(10, "S"), "S")
        .rotate(0.25)
        .f(1)
        .ch(phototype(f.a.r, 1.5, 105, 30
            , fill=hsl(0.17, 0.8, 0.65))))