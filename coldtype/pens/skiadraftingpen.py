import skia
from coldtype.pens.draftingpen import DraftingPen

class SkiaDraftingPen(DraftingPen):
    def __init__(self, path:skia.Path):
        self.path = path
        super().__init__()
    
    @property
    def _value(self):
        def unwrap(p):
            return [p.x(), p.y()]
        
        value = []

        for verb, points in self.path:
            ps = [unwrap(p) for p in points]
            if verb == skia.Path.kMove_Verb:
                value.append(["moveTo", ps])
            elif verb == skia.Path.kLine_Verb:
                value.append(["lineTo", ps[1:]])
            elif verb == skia.Path.kQuad_Verb:
                value.append(["qCurveTo", ps[1:]])
            elif verb == skia.Path.kCubic_Verb:
                value.append(["curveTo", ps[1:]])
            elif verb == skia.Path.kClose_Verb:
                value.append(["closePath", []])
            else:
                raise Exception("Unhandled verb", verb)
        
        return value


from coldtype.pens.draftingpens import DraftingPens
from coldtype.text import Style
import drawbot_skia.drawbot as db

# temp

def StyledString_db(text:str, style:Style):
    db.font(str(style.font.path))
    db.fontSize(style.fontSize)
    if style.features:
        db.openTypeFeatures(**style.features)
    if style.variations:
        db.fontVariations(**style.variations)

    # TODO tracking, custom kerning, etc.

    info = db.glyphs(text)
    
    out = DraftingPens([])
    for gi in info:
        if gi.path:
            p = skia.Path(gi.path)
            p.offset(gi.pos[0], gi.pos[1])
            sdp = SkiaDraftingPen(p)
            sdp.glyphName = gi.name
            out.append(sdp)
    
    return out