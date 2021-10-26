import os, struct
from fontTools.ttLib import TTFont, ttFont
from fontTools.pens.recordingPen import RecordingPen
from .baseFont import BaseFont
from .glyphDrawing import GlyphDrawing
from ..misc.hbShape import HBShape
from ..misc.properties import cachedProperty

import skia
from coldtype.text.dbskia.font import makeTTFontFromSkiaTypeface
from coldtype.text.dbskia.shaping import makeHBFaceFromSkiaTypeface
from coldtype.pens.skiapathpen import SkiaPathPen


class SkiaFont(BaseFont):
    def __init__(self, fontPath, fontNumber, dataProvider=None):
        super().__init__(fontPath, fontNumber)
        self._intermediate_var = None
        self.skiaTypeface = skia.Typeface.MakeFromFile(os.fspath(fontPath))
        self.skiaFont:skia.Font = None

    def load(self, outputWriter):
        self.ttFont = makeTTFontFromSkiaTypeface(self.skiaTypeface)
        self.hbFace = makeHBFaceFromSkiaTypeface(self.skiaTypeface)
        self.shaper = HBShape(self.hbFace, ttFont=self.ttFont)

    def _getGlyphDrawing(self, glyphName, gid, fontSize, colorLayers):
        if self._intermediate_var:
            self.applyVarLocation(self._intermediate_var, fontSize)
        self._intermediate_var = None

        #return GlyphDrawing([(RecordingPen(), None)])

        path = self.skiaFont.getPath(gid)
        return GlyphDrawing([(path, None)])

        # if colorLayers and "COLR" in self.ttFont:
        #     colorLayers = self.ttFont["COLR"].ColorLayers
        #     layers = colorLayers.get(glyphName)
        #     if layers is not None:
        #         drawingLayers = []
        #         for layer in layers:
        #             if self.cocoa:
        #                 drawingLayers.append((self.ftFont.getOutlinePath(layer.name), layer.colorID))
        #             else:
        #                 rp = RecordingPen()
        #                 self.ftFont.drawGlyphToPen(layer.name, rp)
        #                 drawingLayers.append((rp, layer.colorID))
        #         return GlyphDrawing(drawingLayers)
        # if self.cocoa:
        #     outline = self.ftFont.getOutlinePath(glyphName)
        #     return GlyphDrawing([(outline, None)])
        # else:
        #     rp = RecordingPen()
        #     self.ftFont.drawGlyphToPen(glyphName, rp)
        #     return GlyphDrawing([(rp, None)])

    def varLocationChanged(self, varLocation):
        self._intermediate_var = varLocation
        return
    
    def applyVarLocation(self, varLocation, fontSize):
        fa = skia.FontArguments()
        # h/t https://github.com/justvanrossum/drawbot-skia/blob/master/src/drawbot_skia/gstate.py
        to_int = lambda s: struct.unpack(">i", bytes(s, "ascii"))[0]
        makeCoord = skia.FontArguments.VariationPosition.Coordinate
        rawCoords = [makeCoord(to_int(tag), value) for tag, value in varLocation.items()]
        coords = skia.FontArguments.VariationPosition.Coordinates(rawCoords)
        fa.setVariationDesignPosition(skia.FontArguments.VariationPosition(coords))
        
        self.skiaFont = skia.Font(self.skiaTypeface.makeClone(fa), fontSize)

    @cachedProperty
    def colorPalettes(self):
        if "CPAL" in self.ttFont:
            palettes = []
            for paletteRaw in self.ttFont["CPAL"].palettes:
                palette = [(color.red/255, color.green/255, color.blue/255, color.alpha/255) for color in paletteRaw]
                palettes.append(palette)
            return palettes
        else:
            return None