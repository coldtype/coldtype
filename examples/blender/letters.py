from coldtype import *
from coldtype.blender import *
from coldtype.fx.skia import potrace

@b3d_animation(timeline=26, center=(0, 0))
def letters(f):
    return (StSt(chr(f.i+65),
        Font.Find("CompadreV"), 1000, wdth=0)
        .translate(0, 200)
        .f(1)
        .pen()
        .ch(b3d(lambda bp: bp
            .extrude(0.01)
            .rotate(45))))

#@animation(timeline=26)
def letters_potrace(f):
    return (PS([
        (P(f.a.r).f(0.5)),
        (P(f.a.r)
            .img(letters.frameImg(f.i), f.a.r)
            .ch(potrace(f.a.r))
            .f(0))]))