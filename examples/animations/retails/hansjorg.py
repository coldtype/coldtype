from coldtype import *
from coldtype.raster import *
from string import ascii_lowercase
from random import Random

# adapted from Maurice Meilleur’s adaptation of a 1964 piece by Hansjörg Mayer

futura = Font.Find("PolymathV")

ln = len(ascii_lowercase)-2

def scrambled(seed, split):
    r = Random(seed)
    xs = ''.join(r.sample(ascii_lowercase, len(ascii_lowercase)))
    return f"{xs[:-split]}\n{xs[-split:]}"

@animation(1920
    , bg=hsl(0.11, 0.70, 0.65)
    , tl=Timeline(ln*8, 12)
    , release=λ.export("h264", loops=2))
def hj(f:Frame):
    s = Scaffold(f.a.r.inset(80)).numeric_grid(1, 17)
    
    e1 = "l"
    e2 = "ceio"

    factor = f.e("seio", 2, rng=(1, 2))

    def row(x):
        right = round(f.adj(x.i*factor).e(e2, 4, rng=(len(ascii_lowercase)-1, 1)))

        a = f.adj(-x.i*factor)
        xs = scrambled(x.i-f.i, right)
        
        return (StSt(xs, futura
            , fontSize=a.e(e1, rng=(50, 150))
            , tu=a.e(e1, rng=(120, -150))
            , wght=a.e(e1, rng=(0.65, 1))
            , opsz=a.e(e1, rng=(0, 1))
            , liga=0
            , slig=0)
            .î(0, λ.align(x.el, "W", tx=0))
            .î(1, λ.align(x.el, "E", tx=0))
            .ch(filmjitter(f.e("l")
                , scale=(10, 10)
                , base=x.i)))

    return (P().enumerate(s, row)
        .f(1)
        .ch(phototype(f.a.r
            , blur=1.5
            , cut=f.e(e1, rng=(140, 50))
            , cutw=40
            , fill=0)))

@animation(1080
    , tl=hj.timeline
    , solo=1
    , release=λ.export("h264", loops=2))
def hj_resize(f):
    return hj.pass_img(f.i).resize(0.5625)