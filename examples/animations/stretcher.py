from coldtype import *

fnt = Font.Cacheable("~/Type/fonts/fonts/eurostile/EurostileExt-Bla.otf")

@animation((1200, 300), timeline=60, bg=0)
def stretcher(f):
    stretch = Style.StretchX(0, S=(1500*f.e(1, rng=(1, 0)), 450), E=(1500*f.e(1), 430))
    print(stretch)
    return (StSt("STRETCH", fnt, 100, mods=stretch)
        .align(f.a.r)
        .f(1))