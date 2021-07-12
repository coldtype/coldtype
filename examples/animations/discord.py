from coldtype import *
from coldtype.fx.skia import phototype, fill

fnt = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
dfnt = Font.Cacheable("~/Type/fonts/fonts/CleftTwinline-MMv0.1.otf")

@animation(timeline=90, bg=1, composites=1)
def discord(f):
    return (DPS([
            (StSt("COLDTYPE", fnt,
                font_size=f.e(1, rng=(250, 20)),
                wdth=f.e("ceio", 1, rng=(1, 0)),
                tu=f.e(1, rng=(-150, 0)), r=1)
                .align(f.a.r)
                .f(1)
                .understroke(sw=15)),
            (StSt("Discord", dfnt, f.e("ceio", 1, rng=(5, 300)))
                .align(f.a.r)
                .pen()
                .removeOverlap()
                .f(1).s(0).sw(5)
                .v(lambda _: f.e(1) > 0.5))])
        .translate(0, f.e("eeio", 1, rng=(y:=400, -y+10)))
        .insert(0, f.last_render(lambda p: p
            .scale(0.995)
            .ch(fill(1))))
        .ch(phototype(f.a.r, blur=1.5, cut=197, cutw=35,
            fill=hsl(f.e(1, rng=(0.65, 0.85))))))