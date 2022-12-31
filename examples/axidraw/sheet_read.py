from coldtype import *
from coldtype.img.skiaimage import SkiaImage
from coldtype.fx.skia import phototype

# res = ["media/DSC01538.JPG", 8, -0.45, -384, -253, 327, 233, 0, 0]
# res = ["media/DSC01539.JPG", 7, -0.45, -1084, -453, 337, 233, -9, 4]
res = ["media/DSC01540.JPG", 8, -0.45, -954, -333, 327, 233, 0, -9, 4]
#res = ["media/DSC01796.JPG", 8, -0.45, -1054, -443, 298, 204, 0, -6, 10]
#res = ["media/DSC02053.JPG", 8, -0.45, -444, -143, 408, 284, 0, -20, -10]
#res = ["media/DSC02309.JPG", 8, -0.5, -354, -33, 443, 304, 0, -20, 20]
#res = ["media/DSC02565.JPG", 8, 0, -327, -80, 435, 302, -40, -10, 37]
#res = ["media/DSC02821.JPG", 8, -0.5, -327, -180, 378, 258, 0, 0, 0]
#res = ["media/DSC03077.JPG", 8, -0.75, -688, -448, 318, 219, 0, 0, 0]

imgp, sq, ro, xo, yo, xa, ya, xra, xf, yf = res
img = __sibling__(imgp)

@animation((540, 540), tl=Timeline(sq**2, 14), bg=0)
def scratch_C_color1(f):
    x = f.i%sq
    y = f.i//sq
    
    xe = x/sq
    ye = y/sq

    return (P(
        SkiaImage(img)
            .rotate(ro, point=Point(0,0))
            .t(xo-(x*xa)+xe*xf+ye*xra, yo-(y*ya)+xe*yf),
        #StSt("A", Font.MuSan(), 447, wdth=0).align(f.a.r)
        #P(f.a.r.take(60, "C")).outline()
    )
    #.ch(phototype(f.a.r, blur=0, cut=102, cutw=26, fill=1))
    )