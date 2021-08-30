from coldtype import *
from coldtype.blender import *
from coldtype.fx.skia import potrace, phototype

@b3d_animation(timeline=26, center=(0, 0))
def letters(f):
    return (StSt(chr(f.i+65),
        Font.Find("CompadreV"), 1000, wdth=0)
        .align(f.a.r)
        .f(1)
        .pmap(lambda p: p
            .ch(b3d(lambda bp: bp
                .extrude(0.01)
                .rotate(45)
                , zero=True
                ))))

#@animation(timeline=26)
def letters_potrace(f):
    return (DPS([
        (DP(f.a.r).f(0.5)),
        (DP(f.a.r)
            .img(letters.frame_img(f.i), f.a.r)
            .ch(potrace(f.a.r))
            .f(0)
            )]))