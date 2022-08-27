from coldtype import *

from blackrenderer.render import renderText
from blackrenderer.backends.pathCollector import AnnotatedRecordingPen

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

        #print(r.info.name)

        layers = r.layers
        if isinstance(layers, AnnotatedRecordingPen):
            layers = [r.layers]

        if len(layers) == 1 and layers[0].method == "drawPathSolid": # trad font
            glyph.record(layers[0]).f(layers[0].data["color"])
        else:
            for layer in layers: # COLR
                layerGlyph = P().record(layer)
                if layer.method == "drawPathSolid":
                    layerGlyph.f(layer.data["color"])
                else:
                    gradientGlyph = P()
                    if layer.method == "drawPathLinearGradient":
                        (gradientGlyph
                            .line([layer.data["pt1"], layer.data["pt2"]])
                            .fssw(-1, 0, 2).translate(frame.x, 0))
                    elif layer.method == "drawPathSweepGradient":
                        gradientGlyph.moveTo(layer.data["center"])
                    elif layer.method == "drawPathRadialGradient":
                        gradientGlyph.line([layer.data["startCenter"], layer.data["endCenter"]])
                    else:
                        print(">", layer.method)
                        gradientGlyph.rect(frame)
                    
                    (layerGlyph
                        .f(-1)
                        .attr(COLR=[layer.method, layer.data])
                        .data(substructure=gradientGlyph))
                
                glyph.append(layerGlyph)
        
        glyphs.append(glyph)
        x += r.info.xAdvance
    
    return glyphs.scale(style.fontSize/1000, point=(0,0))

@animation((1380, 720), tl=30, bg=1)
def test1(f):
    font = Font.MutatorSans()
    font = Font.Find("PappardelleParty-VF")
    font = Font.Find("Foldit_w")
    font = Font.Find("glyf_colr_1")

    text = "ABC"
    #text = "󰈀" #󰨚
    text = "󰔈"

    br = (BR(text, Style(font
            #, fontSize=1000
            , fontSize=f.e(r=(200, 800))
            #, SPIN=f.e("l")
            #, wdth=f.e()
            , wght=f.e(r=(1, 0))))
            .align(f.a.r, x="CX", th=0, tv=0)
            )

    indicators = P()
    for g in br:
        for p in g:
            colr = p.attr("COLR")
            #colr[1]["colorLine"] = [(0, hsl(0.6, 0.7, 0.3)), (1, hsl(0.9, 0.7, 0.7))]
            indicators.append(p.data("substructure"))
    
    return P(
        br,
        #indicators.s(hsl(0, 1, 0.5, a=0.75)).sw(2)
        )