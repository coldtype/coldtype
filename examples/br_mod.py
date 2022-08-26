from coldtype import *
from blackrenderer.render import renderText

from fontTools.misc.transform import Transform

def BR(text, style):
    results = renderText(style.font.path, text, None,
        returnResult=True,
        backendName="paths",
        fontSize=1000,
        features=style.features,
        variations=style.variations)
    
    glyphs = P()
    x = 0

    for r in results:
        frame = Rect(x+r.info.xOffset, r.info.yOffset, r.info.xAdvance, style._asc)
        glyph = P().data(glyphName=r.info.name, frame=frame)
        if len(r.layers) == 1: # trad font
            glyph.record(r.layers[0]).f(r.layers[0].data["color"])
        else:
            for layer in r.layers: # COLR
                layerGlyph = P().record(layer)
                if layer.method == "drawPathSolid":
                    layerGlyph.f(layer.data["color"])
                else:
                    layerGlyph.f(-1)
                    layer.data["gradientTransform"] = layer.data["gradientTransform"].translate(frame.x)
                    layerGlyph.attr(COLR=[layer.method, layer.data])
                glyph.append(layerGlyph)
        
        glyphs.append(glyph)
        x += r.info.xAdvance
    
    return glyphs.scale(style.fontSize/1000, point=(0,0))

@animation((1380, 720), tl=30, bg=1)
def test1(f):
    font = Font.MutatorSans()
    font = Font.Find("PappardelleParty-VF")
    font = Font.Find("Foldit_w")

    text = "ZEE"

    br = (BR(text, Style(font
            , fontSize=1000
            , SPIN=f.e("l")
            , wdth=f.e()
            , wght=f.e(r=(1, 0))))
            #.align(f.a.r, x="CX", th=0, tv=0)
            )

    return (br
        .layer(
            #lambda ps: ps.map(lambda p: P(p.ambit(th=0, tv=0).inset(2))).fssw(-1, hsl(0.7), 2),
            #lambda ps: ps,#.f(hsl(0.85))
            lambda ps: ps.scale(0.25, point=(0,0)).translate(0, 0)#.align(f.a.r)
            ))