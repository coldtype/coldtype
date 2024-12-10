from coldtype import *
from coldtype.raster import *

@animation(bg=0, tl=60)
def rgbsplit(f):
    return (StSt("COLD\nTYPE", Font.ColdObvi()
        , multiline=1
        , fontSize=f.e(rng=(600, 360))
        , ro=1
        , rotate=f.e("eei", rng=(10, 0))
        , wdth=f.e("eei")
        , leading=f.e("eeo", rng=(10, 50))
        , tu=f.e("eeio", rng=(-70, 0)))
        .xalign(f.a.r)
        .align(f.a.r)
        .reverse(recursive=1)
        .layer(
            lambda p: p.t(d:=f.e(rng=(20, 30)),-d).f("g"),
            lambda p: p.fssw(-1, "b", 20),
            lambda p: p.fssw("r", "b", 6))
        .ch(rgbmod(f.a.r
            , r=lambda x: x
                .ch(filmjitter(f.e("l", 0), 0, scale=(5, 6)))
                .ch(phototype(f.a.r, 1.5, 120, 45, fill=hsl(1.90,0.90,0.75)))
            , g=lambda x: x
                .ch(filmjitter(f.e("l", 0), 1, scale=(5, 6)))
                .ch(phototype(f.a.r, 3, 170, 15, fill=hsl(0.37,0.8,0.75))))))
