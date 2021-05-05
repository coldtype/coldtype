from random import randint
from coldtype import *
from fontTools.ttLib import TTFont
from coldtype.pens.datimage import DATImage
import skia

lh = Font.Cacheable("~/Type/fonts/fonts/liebeheide-color.otf")
ttfont = TTFont(lh.path)

sbix = ttfont["sbix"]
#max_ppem = min(sbix.strikes.keys())
max_ppem = 512
strike = sbix.strikes[max_ppem]

glyphs = {}
for bitmap in strike.glyphs.values():
    if bitmap.graphicType == "png ":
        glyphs[bitmap.glyphName] = bitmap

@renderable(bg=0.5)
def test_leibeheide(r):
    txt = (StyledString("Okey",
        Style(lh, int(512)))
        .pens()
        #.align(r)
        .translate(200, 200)
        .s(0).sw(30))
    
    txt.pmap(lambda i, p: p.s(hsl(random())))

    imgs = DPS()
    for pen in txt:
        g = glyphs[pen.glyphName]
        if g.originOffsetX != 0 or g.originOffsetY != 0:
            raise Exception("non-zero origin")
        print(g.glyphName)
        img = skia.Image.MakeFromEncoded(g.imageData)
        di = DATImage(img)
        imgs.append(di.translate(pen.ambit(th=1).x, 500))
    
    #print(txt[1].ambit(th=1, tv=1).w, imgs[1].bounds().w)
    
    return DPS([
        txt.frameSet(),
        txt,
        DP(txt[0].ambit(th=1, tv=1)).f(0, 0.1),
        #DP(imgs[0].bounds()).f(hsl(0.3, a=0.3)),
        imgs.precompose(r)
    ])

    # return (DPS([
    #     DP(r).f(1),
    #     DPS([
    #             DP(r).f(0),
    #             imgs.precompose(r).blendmode(skia.BlendMode.kXor)
    #         ]).precompose(r)
    #     ])  
    #     .precompose(r)
    #     .phototype(r, blur=0, cut=50)
    #     #.attr(skp=dict(ColorFilter=skia.LumaColorFilter.Make()))
    #     #.precompose(r)
    #     )

    # return (DP(r).f(hsl(0.9)) + (DPS([
            
    #     ])
    #     )).precompose(r)
    #     .attr(skp=dict(
    #         #ImageFilter=skia.BlurImageFilter.Make(10, 10),
    #         ColorFilter=skia.LumaColorFilter.Make()
    #     )))
    
    #return txt[0].align(r).skeleton()
    return txt.translate(0, 660).f(0)#.align(r)
    print(txt.ambit(), DP(txt.ambit()).align(r).ambit())
    return DP(txt.ambit())