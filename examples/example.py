from coldtype import *

@renderable(rect=(900, 500))
def coldtype(r):
    return (StSt("COLDTYPE", Font.ColdObvi()
        , fontSize=450
        , wdth=1
        , tu=-50
        , r=1
        , ro=1
        , fit=r.w)
        .align(r)
        .mape(lambda e, p: (p
            .f(hsl(0.5+e*0.15, s=0.6, l=0.55))
            .s(0).sw(30).sf(1)))
        .rotate(5)
        .scale(0.75))