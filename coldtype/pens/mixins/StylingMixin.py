from coldtype.runon.runon import Runon
from coldtype.color import Color, normalize_color


class StylingMixin():
    def groupStrokeStyle(self, st):
        if "stroke" in st:
            c = st["stroke"]
            sw = st.get("strokeWidth", 1)
            st["stroke"] = dict(color=c, weight=sw)
        if "strokeWidth" in st:
            del st["strokeWidth"]
        return st

    def f(self, *value):
        """Get/set a (f)ill"""
        if value:
            if not isinstance(value, Color):
                value = normalize_color(value)
            return self.attr(fill=value)
        else:
            return self.attr(field="fill")
    
    fill = f
    
    def s(self, *value):
        """Get/set a (s)troke"""
        if value:
            if not isinstance(value, Color):
                value = normalize_color(value)
            return self.attr(stroke=value)
        else:
            return self.attr(field="stroke")
    
    stroke = s
    
    def sw(self, value):
        """Get/set a (s)troke (w)idth"""
        if value is not None:
            return self.attr(strokeWidth=value)
        else:
            return self.attr(field="strokeWidth")
    
    strokeWidth = sw

    def ssw(self, s, sw):
        self.s(s)
        self.sw(sw)
        return self
    
    def fssw(self, f, s, sw):
        self.f(f)
        self.s(s)
        self.sw(sw)
        return self