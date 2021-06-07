from coldtype import *

fnt = Font.Cacheable("~/Type/fonts/fonts/eurostile/EurostileExt-Bla.otf")

@animation(timeline=60)
def stretcher(f):
    stretch = Style.StretchX(0, S=(500, 450), E=(10000*f.e(1), 430))
    return (StSt("STRETCH", fnt, 100, mods=stretch)
        .align(f.a.r))