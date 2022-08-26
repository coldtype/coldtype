from coldtype import *
from blackrenderer.render import renderText

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
            for layer in r.layers: # COLRv0
                layerGlyph = P().record(layer)
                if layer.method == "drawPathSolid":
                    layerGlyph.f(layer.data["color"])
                glyph.append(layerGlyph)
        
        glyphs.append(glyph)
        x += r.info.xAdvance
    
    return glyphs.scale(style.fontSize/1000, point=(0,0))

@animation((1080, 540), tl=30, bg=1)
def test1(f):
    font = Font.MutatorSans()
    #font = Font.Find("PappardelleParty-VF")
    font = Font.Cacheable("~/Type/Typeworld/color-fonts/fonts/twemoji-cff_colr_1.otf")

    text = "TEXT"
    text = "🍥"

    br = BR(text, Style(font
            , fontSize=300
            , SPIN=f.e("l")
            , wdth=f.e()
            , wght=f.e(r=(1, 0))))

    return (br
        .align(f.a.r, th=0, tv=0)
        .layer(
            lambda ps: ps.map(lambda p: P(p.ambit(th=0, tv=0).inset(2))).fssw(-1, hsl(0.7), 2),
            lambda ps: ps#.f(hsl(0.85))
            ))