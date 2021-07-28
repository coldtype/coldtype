from coldtype import *
from coldtype.blender import *
from coldtype.fx.skia import potrace, phototype, luma
#from coldtype.img.skiaimage import SkiaImage

@b3d_animation(timeline=26)
def letters(f):
    return (StSt(chr(f.i+65), Font.Find("CompadreV"), 1000)
        .align(f.a.r)
        .pen()
        .tag("letter")
        .f(1)
        .ch(b3d("Text", lambda bp: bp
            .extrude(2)
            .locate(0, 0, 0)
            .rotate(0)
            .with_origin("C", lambda bp: bp.rotate(15, 0, 0))
            )))

@animation(timeline=26)
def letters_potrace(f):
    return (DPS([
        (DP(f.a.r).f(1)),
        (DP(f.a.r)
            .img(letters.blender_rendered_frame(f.i), f.a.r, False)
            .ch(phototype(f.a.r, blur=2, fill=0, cut=180)))])).ch(luma(f.a.r))