from coldtype.color import Color, normalize_color, rgb
from coldtype.geometry import Rect

"""
Requires Runon.attr contract
"""

class StylingMixin():
    def groupedStyle(self, st):
        if "stroke" in st:
            c = st["stroke"]
            sw = st.get("strokeWidth", 1)
            st["stroke"] = dict(color=c, weight=sw)
        if "strokeWidth" in st:
            del st["strokeWidth"]

        if "fill" not in st:
            st["fill"] = rgb(1, 0, 0.5)
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
    
    def img(self, src=None, rect=Rect(0, 0, 500, 500), pattern=False, opacity=1.0):
        """Get/set an image fill"""
        if src:
            from coldtype.img.datimage import DATImage
            if isinstance(src, DATImage):
                return self.attr(image=dict(src=src.src, rect=rect, pattern=pattern, opacity=opacity))
            return self.attr(image=dict(src=src, rect=rect, pattern=pattern, opacity=opacity))
        else:
            return self.attr(field="image")
    
    image = img

    def shadow(self, radius=10, color=(0, 0.3), clip=None):
        return self.attr(shadow=dict(color=normalize_color(color), radius=radius, clip=clip))