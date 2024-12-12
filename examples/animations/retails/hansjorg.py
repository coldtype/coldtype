from coldtype import *
from coldtype.raster import *
from string import ascii_lowercase
from random import Random

futura = Font.Find("Futura", number=2)
futura = Font.Find("PolymathV")

ln = len(ascii_lowercase)-2

@animation(1920, bg=hsl(0.91, 0.50, 0.55), tl=Timeline(ln*8, 12))
def hj(f):
    s = Scaffold(f.a.r.inset(30)).numeric_grid(1, 17)
    
    fs = f.e("l", rng=(60, 170))
    tu = f.e("l", rng=(120, -150))
    wght = f.e("l", rng=(0.65, 1))
    cut = f.e("l", rng=(140, 50))

    def row(x):
        right = round(f.adj(x.i).e("l", 4, rng=(len(ascii_lowercase)-1, 1)))

        xs = [*ascii_lowercase]
        r = Random()
        r.seed(x.i-f.i)
        r.shuffle(xs)
        
        return (P(
            StSt("".join(xs[:len(ascii_lowercase)-right]), futura, fs, tu=tu, liga=0, wght=wght)
                .align(x.el, "W"),
            StSt("".join(xs[len(ascii_lowercase)-right:]), futura, fs, tu=tu, liga=0, wght=wght)
                .align(x.el, "E"))
            .ch(filmjitter(f.e("l"), scale=(10, 10), base=x.i)))

    return (P().enumerate(s, row)
        .f(1)
        .ch(phototype(f.a.r, 1.5, cut, 40, fill=0)))