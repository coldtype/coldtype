import os
from fontTools.ufoLib import UFOReader
from fontTools.ufoLib.glifLib import Glyph


if __name__ == "__main__":
    import sys
    dirname = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(f"{dirname}/..")

from coldtype.pens.datpen import DATPen, OpenPathPen
from coldtype.geometry import Rect


class UFOStringSetter():
    def __init__(self, path):
        self.path = os.path.expanduser(path)
        self.ufo = UFOReader(self.path)
        info = {}
        self.info = self.ufo._readInfo(False)
        self.glyphSet = self.ufo.getGlyphSet() # send in minimal options here?
    
    def getGlyph(self, glyphName):
        return self.glyphSet[glyphName]
    
    def getGlyphs(self, glyphNames):
        if isinstance(glyphNames, str):
            names = glyphNames.split(" ")
        else: # iterable
            names = glyphNames
        od = []
        for name in names:
            od.append(self.getGlyph(name))
        return od
    
    def getLine(self, string, atomized=False, typographic=True):
        glyphs = self.getGlyphs(string)
        pens = []
        offset = 0
        for glyph in glyphs:
            dp = DATPen()
            op = OpenPathPen(dp)
            glyph.draw(op)
            dp.translate(offset, 0)
            if typographic:
                dp.addFrame(Rect(offset, 0, glyph.width, self.info.get("capHeight", 750)), typographic=typographic)
            offset += glyph.width
            pens.append(dp)
        if atomized:
            return pens
        else:
            full_frame = Rect(*pens[0].frame) # naive
            full_frame.w = pens[-1].frame.x + pens[-1].frame.w
            dp = DATPen()
            for pen in pens:
                dp.record(pen)
            if typographic:
                dp.addFrame(full_frame)
            return dp


if __name__ == "__main__":
    from coldtype.viewer import viewer
    from coldtype.pens.svgpen import SVGPen
    with viewer() as v:
        r = Rect(0, 0, 500, 500)
        uss = UFOStringSetter("~/Type/drawings/GhzGong/GhzGong.ufo")
        #pens = uss.getLine("G o_o d h e_r t_z")
        dp = uss.getLine("goodhertz.gordy.copy_1")
        #dp = uss.getLine("G o_o d")
        dp.addAttrs(fill=None, stroke="random")
        #dp.frame = None
        #dp.typographic = False
        dp.scaleToRect(r.inset(10, 10))
        dp.align(r)
        v.send(SVGPen.Composite([dp], r), r)