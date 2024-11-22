from coldtype import *
from coldtype.img.skiaimage import SkiaImage
from coldtype.fx.skia import phototype, precompose

# res = ["media/DSC01538.JPG", 8, -0.45, -384, -253, 327, 233, 0, 0]
# res = ["media/DSC01539.JPG", 7, -0.45, -1084, -453, 337, 233, -9, 4]
res = ["/Users/robstenson/Sites/othermodern.com/media/_goodhertz/hires/Capture One Catalog01461RAW lossless compressed.jpg", 8, -0.45, -954, -333, 327, 233, 0, -9, 4]
#res = ["media/DSC01796.JPG", 8, -0.45, -1054, -443, 298, 204, 0, -6, 10]
#res = ["media/DSC02053.JPG", 8, -0.45, -444, -143, 408, 284, 0, -20, -10]
#res = ["media/DSC02309.JPG", 8, -0.5, -354, -33, 443, 304, 0, -20, 20]
#res = ["media/DSC02565.JPG", 8, 0, -327, -80, 435, 302, -40, -10, 37]
#res = ["media/DSC02821.JPG", 8, -0.5, -327, -180, 378, 258, 0, 0, 0]
#res = ["media/DSC03077.JPG", 8, -0.75, -688, -448, 318, 219, 0, 0, 0]
#res = ["/Users/robstenson/Pictures/SigmaFPLTetherTest1/Output/SigmaFPLTetherTest10002 1 2.jpg", 8, 0, -684, -133, 912, 703, 0, -9, 4]

imgp, sq, ro, xo, yo, xa, ya, xra, xf, yf = res

@animation((1080, 1080), tl=Timeline(16*16, 18), bg=1)
def sheet_read(f):
    img = SkiaImage(ººsiblingºº(imgp))

    x = f.i%16
    y = f.i//16
    
    xe = x/sq
    ye = y/sq

    return (P(
        img
            .t(-271, -5080)
            .t(x*-468, y*357)
            #.in_pen(),
            #.rotate(ro, point=Point(0,0))
            #.t(xo-(x*xa)+xe*xf+ye*xra, yo-(y*ya)+xe*yf),
        #StSt("A", Font.MuSan(), 447, wdth=0).align(f.a.r)
        #P(f.a.r.take(60, "C")).outline()
    )
    #.layer(1, lambda _: P(f.a.r).f(1).blendmode(BlendMode.Difference))
    #.ch(precompose(f.a.r))
    #.ch(phototype(f.a.r, blur=0, cut=172, cutw=26, fill=1))
    )