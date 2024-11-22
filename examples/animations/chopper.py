from coldtype import *
from coldtype.raster import *

from functools import partial

def Chopper(**kwargs):
    d = {}
    
    def chopper(n, s, e, w, i, p):
        amb = p.ambit(tx=0, ty=0)
        return p.intersection(P(amb.drop(n, "N", forcePixel=1).drop(s, "S", forcePixel=1).drop(e, "E", forcePixel=1).drop(w, "W", forcePixel=1))).translate(-w, 0)#.record(P(amb).outline(2).reverse())
    
    for k, v in kwargs.items():
        d[k] = (-(v[2]+v[3]), partial(chopper, v[0], v[1], v[2], v[3]))
    
    return d

rsc = random_series()

@animation((1080, 1080), tl=160, bg=0)
def chopper(f):
    e = f.io([40, 40])
    ##d = 140*f.e("eeo")
    stx = Chopper(
        O=(0,0,120*e,120*e),
        C=(0,0,140*e,110*e),
        M=(0,0,100*e,80*e),
        P=(0,0,140*e,117*e),
        R=(0,0,120*e,180*e),
        E=(0,0,80*e,140*e),
        S=(0,0,140*e,140*e),
        )
    
    return (StSt("COMPRESS".upper()
        , "Hex Franklin v0.3 Tyght V"
        , fontSize=f.io([60, 60], rng=(195, 900))
        , NOTC=1
        , TYTE=0
        , mods=stx
        , tu=f.e("eeio", rng=(210, 10))
        , kp={
            "O/M":-10*e,
            "M/P":-11*e,
            "R/E":-7*e,
            "P/R":-6*e,
            "E/S":9*e
        }
        #, wght=0.75
        , wdth=0
        #, tu=10
        )
        .mapv(lambda i, p: p.f(hsl(rsc[i], 0.5)).up().___insert(0, lambda x: P(x.ambit()).fssw(hsl(rsc[i], 0.5, 0.8, 0.3), 0, 1)))
        #.track(10)
        .align(f.a.r)
        .f(1)
        #.ch(shake(2, 1, seed=0))
        .ch(filmjitter(f.e("l"), scale=(2,2)))
        .ch(phototype(f.a.r, 2, 160, 30, fill=1))
        )
