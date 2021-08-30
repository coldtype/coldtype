from coldtype import *
from coldtype.blender import *
from coldtype.fx.skia import potrace, phototype, luma
#from coldtype.img.skiaimage import SkiaImage

@b3d_animation(timeline=26, center=(0, 0))
def letters(f):
    return (StSt(chr(f.i+65),
        Font.Find("CompadreV"), 1000, wdth=0)
        .align(f.a.r)
        #.pen()
        .f(1)
        .pmap(lambda p: p
            .ch(b3d(lambda bp: bp
                .extrude(0.25)
                #, dn=True
                , zero=True
                ))
            .ch(b3d_post(lambda bp: bp
                .rotate(45)))))

#@animation(timeline=26)
def letters_potrace(f):
    return (DPS([
        (DP(f.a.r).f(1)),
        (DP(f.a.r)
            .img(letters.frame_img(f.i), f.a.r, False)
            .ch(phototype(f.a.r, blur=2, fill=0, cut=180)))])).ch(luma(f.a.r))