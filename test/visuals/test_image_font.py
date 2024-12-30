from coldtype import *
from coldtype.img.skiaimage import SkiaImage
from coldtype.fx.skia import skia, precompose

lh = Font.Find("liebe")
ttfont = lh.font.ttFont

sbix = ttfont["sbix"]
print(sbix.strikes.keys())
#max_ppem = min(sbix.strikes.keys())
max_ppem = 512
strike = sbix.strikes[max_ppem]

glyphs = {}
for bitmap in strike.glyphs.values():
    if bitmap.graphicType == "png ":
        glyphs[bitmap.glyphName] = bitmap

@renderable(bg=0)
def test_leibeheide(r):
    txt = (StSt("Okey", lh, int(512), metrics="a")
        .align(r, ty=1)
        .f(0)
        .s(0)
        .sw(117)
        .mapv(lambda p: p.s(hsl(random()))))
    
    #print(txt[0]._val.value)
    #return P(txt[0]) + P(txt[0].ambit()).fssw(-1, 0, 1)

    imgs = P()
    for pen in txt:
        g = glyphs[pen.glyphName]
        if g.originOffsetX != 0 or g.originOffsetY != 0:
            raise Exception("non-zero origin")
        
        print(g.glyphName)
        img = skia.Image.MakeFromEncoded(g.imageData)
        di = SkiaImage(img)
        #di.write("test.png")
        imgs.append(di.translate(pen.ambit(tx=1).x, pen.ambit(ty=1).y))
    
    return P(
        #txt.frameSet(),
        txt,
        #DP(txt[0].ambit(tx=1, ty=1)).f(0, 0.1),
        #DP(imgs[0].bounds()).f(hsl(0.3, a=0.3)),
        imgs.ch(precompose(r)).blendmode(BlendMode.Cycle(36))
        )
    
    #return txt[0].align(r).skeleton()
    return txt.translate(0, 660).f(0)#.align(r)
    print(txt.ambit(), DP(txt.ambit()).align(r).ambit())
    return DP(txt.ambit())