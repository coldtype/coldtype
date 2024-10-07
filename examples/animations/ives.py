from coldtype import *
from coldtype.fx.skia import phototype

VERSIONS = {
    2: dict(),
    3: dict(),
    4: dict(),
    5: dict(),
    6: dict(),
    7: dict(),
    8: dict(),
    9: dict(),
    10: dict(),
    11: dict(),
    12: dict(),
    13: dict(),
    14: dict(),
    15: dict(),
    16: dict(),
    17: dict(),
    18: dict(),
    19: dict(),
    20: dict(),
    21: dict(),
    22: dict(),
    23: dict(),
    24: dict(),
    25: dict(),
    26: dict(),
} #/VERSIONS

d = __VERSION__["key"]

letters = "COLDTYPE"*4000
rsx = random_series(-80, 80, d)
rsy = random_series(-80, 80, d)
rsw = random_series(seed=d)
rswd = random_series(seed=d)
rsr = random_series(0, 10, d)
rsa = random_series(-30, 30, d)

@animation((1080, 1080), bg=1, tl=100)
def grid_ƒVERSION(f):
    s = Scaffold.AspectGrid(f.a.r.inset(30), d, d, "N")
    return (P().enumerate(s, lambda x:
        StSt(letters[x.i], Font.MuSan(), f.adj(rsa[x.i]).e("eeio", 3, rng=(100, 500)), wght=rsw[x.i], wdth=rswd[x.i])
            .align(x.el)
            .rotate(int(rsr[x.i])*180+f.adj(rsa[x.i]).e("eeio", 2, rng=(0, 270)), x.el.pc)
            .translate(rsx[x.i], rsy[x.i])
            .intersection(P(x.el))
            .f(1))
        .insert(0, s.borders().fssw(-1, 1, 5))
        .ch(phototype(f.a.r, 2, 127, 18, fill=bw(0))))