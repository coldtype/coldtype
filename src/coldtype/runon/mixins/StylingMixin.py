from coldtype.color import Color, Theme, normalize_color, rgb
from coldtype.geometry import Rect
from coldtype.img.blendmode import BlendMode

"""
Requires Runon.attr contract
"""

class StylingMixin():
    def groupedStyle(self, st, default_style):
        sf = False
        if "stroke" in st:
            c = st["stroke"]
            sw = st.get("strokeWidth", default_style.get("strokeWidth", 1))
            miter = st.get("strokeMiter", default_style.get("strokeMiter", None))
            st["stroke"] = dict(color=c, weight=sw, miter=miter)
        
        if "stroke" not in st and "stroke" in default_style:
            st["stroke"] = self.groupedStyle(default_style, default_style)["stroke"]
        
        if "strokeWidth" in st:
            del st["strokeWidth"]
        if "strokeMiter" in st:
            del st["strokeMiter"]
        if "strokeFirst" in st:
            sf = True
            del st["strokeFirst"]
        
        if "fill" not in st:
            st["fill"] = rgb(1, 0, 0.5)
        
        rest = ["blendmode", "image", "skp", "COLR", "dash"]
        if sf:
            order = ["shadow", "stroke", "fill", *rest]
        else:
            order = ["shadow", "fill", "stroke", *rest]
        
        sort = {k:v for k,v in sorted(st.items(), key=lambda kv: order.index(kv[0]))}
        return sort

    def f(self, *value):
        """Get/set a (f)ill"""
        if value:
            if isinstance(value[0], Theme):
                for k, v in value[0].colors.items():
                    self.attr(k, fill=v)
                return self
            elif not isinstance(value, Color):
                value = normalize_color(value)
            return self.attr(fill=value)
        else:
            return self.attr(field="fill")
    
    fill = f
    
    def s(self, *value):
        """Get/set a (s)troke"""
        if value:
            if isinstance(value[0], Theme):
                for k, v in value[0].colors.items():
                    self.attr(k, stroke=v)
                return self
            elif not isinstance(value, Color):
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

    def dash(self, pattern, phase=0):
        return self.attr(dash=[pattern, phase])

    def ssw(self, s, sw):
        self.s(s)
        self.sw(sw)
        return self
    
    def fssw(self, f, s, sw, sf=0):
        self.f(f)
        self.s(s)
        self.sw(sw)
        self.sf(sf)
        return self
    
    def strokeFirst(self, value=None):
        """
        For a rendering engine that has to stroke and fill in two separate passes, perform the stroke _before_ the fill (akin to an `.understroke` but without the duplication overhead)
        """
        if value:
            return self.attr(strokeFirst=value)
        else:
            return self.attr(field="strokeFirst")
    
    def sf(self, value=None):
        "strokeFirst"
        return self.strokeFirst(value)
    
    def strokeMiter(self, value=None):
        """
        For a rendering engine that can specify stroke-miter
        """
        if value:
            return self.attr(strokeMiter=value)
        else:
            return self.attr(field="strokeMiter")

    def sm(self, value=None):
        "strokeMiter"
        return self.strokeMiter(value)
    
    def img(self, src=None, rect=Rect(0, 0, 500, 500), pattern=False, opacity=1.0):
        """Get/set an image fill"""
        if src:
            from coldtype.img.abstract import AbstractImage
            if isinstance(src, AbstractImage):
                return self.attr(image=dict(src=src.src, rect=rect, pattern=pattern, opacity=opacity))
            return self.attr(image=dict(src=src, rect=rect, pattern=pattern, opacity=opacity))
        else:
            return self.attr(field="image")
    
    image = img

    def shadow(self, radius=10, color=(0, 0.3), clip=None):
        return self.attr(shadow=dict(color=normalize_color(color), radius=radius, clip=clip))
    
    # other

    def blendmode(self, blendmode=None, show=False):
        if isinstance(blendmode, int):
            blendmode = BlendMode.Cycle(blendmode, show=show)
        elif isinstance(blendmode, str):
            blendmode = BlendMode[blendmode]
        
        if blendmode:
            return self.attr(blendmode=blendmode)
        else:
            return self.attr(field="blendmode")
    
    def postprocess(self, fn):
        return self.data(postprocess=fn, function_literals=True)