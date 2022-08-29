from coldtype import *

#from blackrenderer.render import getLineGlyphs, buildLineInfo, BlackRendererFont
#from blackrenderer.backends.pathCollector import PathCollectorRecordingPen

def buildLayeredGlyph(glyph, layer, frame):
    layerGlyph = P().record(layer)
    glyph.append(layerGlyph)

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

def BR(text, style):
    font = BlackRendererFont(style.font.path)
    info = buildLineInfo(font, text,
        lang=style.lang,
        #script=style.script,
        features=style.features,
        variations=style.variations)
    results = getLineGlyphs(font, info)
    
    glyphs = P()
    x = 0

    for r in results:
        frame = Rect(
            x + r.info.xOffset,
            r.info.yOffset,
            r.info.xAdvance,
            style._asc)
        
        glyph = P().data(glyphName=r.info.name, frame=frame)

        layers = r.layers
        if isinstance(layers, PathCollectorRecordingPen):
            if layers.method == "drawPathSolid": # trad font
                glyph.record(layers).f(layers.data["color"])
                layers = None
            else:
                layers = [layers]
        
        if layers:
            for layer in layers:
                buildLayeredGlyph(glyph, layer, frame)
        
        glyphs.append(glyph)
        x += r.info.xAdvance
    
    return glyphs.scale(style.fontSize/1000, point=(0,0))

@animation((1380, 720), tl=30, bg=1)
def test1(f):
    font = Font.MutatorSans()
    font = Font.Find("PappardelleParty-VF")
    font = Font.Find("Foldit_w")
    #font = Font.Find("glyf_colr_1")

    text = "ABC"
    #text = "󰈀" # sweep pie chart thing
    #text = "󰨚" # empty weirdo
    #text = "󰔈" # radial with clip

    br = (StSt(text, font
            , fontSize=f.e(r=(200, 800))
            , wght=f.e(r=(1, 0)))
            .align(f.a.r, x="CX", th=0, tv=0))
    
    return P(
        br,
        #br.substructure()
        )