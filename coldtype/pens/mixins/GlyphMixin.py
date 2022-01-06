

class GlyphMixin():
    def glyph(self, glyph, glyphSet=None):
        """Play a glyph (like from `defcon`) into this pen."""
        if glyphSet:
            self._glyphSet = glyphSet
        glyph.draw(self._val)
        return self
    
    def toGlyph(self, name=None, width=None, allow_blank=False):
        """
        Create a glyph (like from `defcon`) using this pen’s value.
        *Warning*: if path is unended, closedPath will be called
        """
        from defcon import Glyph
        if not allow_blank:
            if self.unended():
                self.closePath()
        bounds = self.bounds()
        glyph = Glyph()
        glyph.name = name
        glyph.width = width or bounds.w
        try:
            sp = glyph.getPen()
            self.replay(sp)
        except AssertionError:
            if not allow_blank:
                print(">>>blank glyph:", glyph.name)
        return glyph