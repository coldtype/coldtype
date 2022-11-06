from coldtype import *

@renderable()
def mirror(r):
    return (StSt("C", Font.ColdObvi(), 300)
        .align(r.inset(100).take(0.5, "NW"))
        .mirrorx(r.pc)
        .mirrory(r.pc)
        .layer(
            lambda p: p.rotate(45, point=r.pc)
                .f(hsl(0.9, 0.8)),
            lambda p: p.f(hsl(0.65, 0.8))))