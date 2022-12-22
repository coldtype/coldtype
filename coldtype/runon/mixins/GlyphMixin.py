from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform


class GlyphMixin():
    def glyph(self, glyph, glyphSet=None, layerComponents=False):
        """Play a glyph (like from `defcon`) into this pen."""
        out = type(self)()
        base = type(self)()
        out.append(base)
        glyph.draw(base._val)

        new_val = []
        for mv, pts in base._val.value:
            if mv == "addComponent":
                component_name, matrix = pts
                rp = RecordingPen()
                tp = TransformPen(rp, Transform(*matrix))
                component = glyphSet[component_name]
                # recursively realize any nested components
                realized = type(self)().glyph(component, glyphSet)
                realized.replay(tp)
                p = type(self)()
                p._val = rp
                out.append(p)
                if "addComponent" in str(p._val.value):
                    print("> NESTED COMPONENT", component_name)
            else:
                new_val.append((mv, pts))
        
        base._val.value = new_val
        
        if layerComponents:
            return out
        else:
            try:
                out.pen().replay(self._val)
            except IndexError:
                pass
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