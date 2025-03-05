from collections import OrderedDict
from functools import partial
from shutil import copy2
from pathlib import Path

import unicodedata, math

from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen

from coldtype.osutil import run_with_check
from coldtype.color import normalize_color, rgb
from coldtype.runon.path import P
from coldtype.geometry import Rect
from coldtype.text.font import Font, normalize_font_path, normalize_font_prefix, FontNotFoundException, ALL_FONT_DIRS, _prefixes

from typing import Union

from fontgoggles.misc.platform import setUseCocoa
setUseCocoa(False)

from fontgoggles.misc.textInfo import TextInfo
from fontgoggles.font.glyphDrawing import GlyphDrawing

import uharfbuzz as hb

try:
    from blackrenderer.font import BlackRendererFont
    #from blackrenderer.backends.pathCollector import PathCollectorSurface, PathCollectorRecordingPen
    from coldtype.text.colr.brsurface import BRPathCollectorSurface, BRPathCollectorRecordingPen
except ImportError:
    BlackRendererFont = None
    pass

class FittableMixin():
    def textContent(self):
        print("textContent() not overwritten")

    def fit(self, width):
        """Use various methods (tracking, `wdth` axis, etc. — properties specified in the `Style` object) to fit a piece of text horizontally to a given `width` (warning: not very fast)"""
        if isinstance(width, Rect):
            width = width.w
        current_width = self.width()
        tries = 0
        if current_width > width: # need to shrink
            while tries < 100000 and current_width > width:
                adjusted = self.shrink()
                if adjusted:
                    tries += 1
                    current_width = self.width()
                else:
                    #print(">>> TOO BIG :::", self.textContent())
                    return self
        elif current_width < width: # need to expand
            pass
        #print(">>>>>>>>>>>>>>>>>> FINAL TRIES", tries)
        return self


class Style():
    """
    Class for configuring font properties

    #### Keyword arguments

    * `font`: can either be a `coldtype.text.Font` object, a `pathlib.Path`, or a plain string path
    * `font_size`: standard point-based font-size, expressed as integer
    * `tracking` (aka `tu`): set the tracking, by default **in font-source-point-size** aka as if the font-size was always 1000; this means tracking is by default done relatively rather than absolutely (aka the relative tracking will not change when you change the font_size)
    * `trackingMode`: set to 0 to set tracking in a classic font_size-based (defaults to 1, as described just above)
    * `space`: set this to override the width of the standard space character (useful when setting text on a curve and the space is getting collapsed)
    * `baselineShift` (aka `bs`): if an integer, shifts glyphs by that amount in y axis; if a list, shifts glyphs at corresponding index in list by that amount in y axis
    * `xShift` (aka `xs`): if an integer, shifts glyphs by that amount in x axis; if a list, shifts glyphs at corresponding index in list by that amount in x axis
    * `rotate`: rotate glyphs by degree
    * `reverse` (aka `r`): reverse the order of the glyphs, so that the left-most glyph is first in when vectorized via `.pens()`
    * `removeOverlaps` (aka `ro`): automatically use skia-pathops to remove overlaps from the glyphs (useful when using variable ttf fonts)
    * `lang`: set language directly, to access language-specific alternate characters/rules

    #### Shorthand kwargs

    * `kp` for `kern_pairs` — a dict of glyphName->[left,right] values in font-space
    * `tl` for `trackingLimit`
    * `bs` for `baselineShift`
    * `ch` for `capHeight` — a number in font-space; not specified, read from font; specified as 'x', capHeight is set to xHeight as read from font
    """
    def RegisterShorthandPrefix(prefix, expansion):
        global _prefixes
        _prefixes.append([prefix, str(expansion)])

    def __init__(self,
        font:Union[Font, str]=None,
        font_size:int=12,
        tracking=0,
        trackingMode=1,
        postTracking=0,
        kern_pairs=dict(),
        space=None,
        baselineShift=0,
        xShift=None,
        rotate=0,
        reverse=False,
        removeOverlap=False,
        q2c=False,
        lang=None,
        narrower=None,
        fallback=None,
        palette=0,
        capHeight=None,
        ascender=None,
        descender=None,
        metrics="c",
        data={},
        layer=None,
        liga=True,
        kern=True,
        fill=rgb(0, 0.5, 1),
        stroke=None,
        strokeWidth=0,
        instance=None,
        variations=dict(),
        variationLimits=dict(),
        trackingLimit=0,
        scaleVariations=True,
        rollVariations=False,
        mods=None,
        features=dict(),
        increments=dict(),
        varyFontSize=False,
        preventHwid=False,
        fitHeight=None,
        meta=dict(),
        no_shapes=False,
        show_frames=False,
        load_font=True, # should we attempt to load the font?
        tag=None, # way to differentiate in __eq__
        annotate=False,
        case=None,
        cluster=False,
        **kwargs
        ):

        self.input = locals()
        self.input["self"] = None

        if load_font:
            self.font = Font.Normalize(font)
        else:
            self.font = font

        self.meta = meta
        self.case = case

        self.cluster = cluster
        self.fallback = fallback
        self.narrower = narrower
        self.layer = layer
        self.reverse = kwargs.get("r", reverse)
        self.removeOverlap = kwargs.get("ro", removeOverlap)
        self.q2c = q2c
        self.rotate = rotate
        self.scaleVariations = kwargs.get("sv", scaleVariations)
        self.rollVariations = kwargs.get("rv", rollVariations)
        self.tag = tag
        self.annotate = annotate
        
        self.metrics = metrics
        self.capHeight = kwargs.get("ch", capHeight)
        self.descender = kwargs.get("dsc", descender)
        self.ascender = kwargs.get("asc", ascender)

        self.no_shapes = no_shapes
        self.show_frames = show_frames

        self.complete_metrics()
        if "c" in self.metrics:
            self._asc = self.capHeight
        else:
            self._asc = self.ascender
        
        # legacy for older code
        if kwargs.get("fontSize"):
            font_size = kwargs.get("fontSize")

        if fitHeight:
            self.fontSize = (fitHeight/self._asc)*1000
        else:
            self.fontSize = font_size
        
        self.fontSize = max(self.fontSize, 0)

        self.postTracking = postTracking
        self.tracking = kwargs.get("t", tracking)
        self.kern_pairs = kwargs.get("kp", kern_pairs)
        self.trackingMode = trackingMode
        self.trackingLimit = kwargs.get("tl", trackingLimit)
        self.baselineShift = kwargs.get("bs", baselineShift)
        self.increments = increments
        self.space = space
        self.xShift = kwargs.get("xs", xShift)
        self.mods = mods
        self.palette = palette
        self.lang = lang
        self.data = data
        self.preventHwid = preventHwid

        if kwargs.get("tu"):
            self.trackingMode = 1 # this is the default now
            self.tracking = kwargs.get("tu")
            if not self.increments.get("tracking"):
                self.increments["tracking"] = 5 # TODO good?

        found_features = features.copy()
        for k, v in kwargs.items():
            if k.startswith("ss") and len(k) == 4:
                found_features[k] = v
            if k in ["dlig", "swsh", "onum", "tnum", "palt", "salt", "vert"]:
                found_features[k] = v
            if k in ["slig"]:
                if k == 0:
                    found_features[k] = 0
        
        self.features = {}
        all_features = {**dict(kern=kern, liga=liga), **found_features}

        if not isinstance(self.font, str):
            # making sure the features exist before we set them
            try:
                gpos = self.font.font.shaper.getFeatures("GPOS")
                gsub = self.font.font.shaper.getFeatures("GSUB")
                for feature, v in all_features.items():
                    if feature in gpos or feature in gsub:
                        self.features[feature] = int(v)
            except Exception as e:
                print("feature finder failed", e)

        self.fill = normalize_color(fill)
        self.stroke = normalize_color(stroke)
        
        if stroke and strokeWidth == 0:
            self.strokeWidth = 1
        else:
            self.strokeWidth = strokeWidth

        unnormalized_variations = variations.copy()

        self.instance = instance
        self.axes = OrderedDict()
        self.variations = dict()
        self.variationLimits = dict()
        self.varyFontSize = varyFontSize

        if not load_font:
            return
        else:
            fvar = self.font.font.ttFont.get("fvar")
            if fvar is not None:
                for axidx, axis in enumerate(sorted(fvar.axes, key=lambda ax: ax.axisTag)):
                    generic = f"fvar_{axidx}"
                    self.axes[axis.axisTag] = axis
                    self.variations[axis.axisTag] = axis.defaultValue
                    if axis.axisTag == "wdth": # the only reasonable default
                        self.variationLimits[axis.axisTag] = axis.minValue
                    if axis.axisTag in kwargs and axis.axisTag not in variations:
                        v = kwargs[axis.axisTag]
                        if v is not None:
                            unnormalized_variations[axis.axisTag] = kwargs[axis.axisTag]
                    if generic in kwargs and axis.axisTag not in variations:
                        unnormalized_variations[axis.axisTag] = kwargs[generic]
            
            if self.instance:
                self.scaleVariations = False
                xs = self.font.instances(scaled=False, search=self.instance)
                if xs:
                    self.addVariations(xs)
                else:
                    self.addVariations(unnormalized_variations)
            else:
                self.addVariations(unnormalized_variations)
    
    def __eq__(self, other):
        try:
            if not self.tag == other.tag:
                return False
            if not self.font == other.font:
                return False
            elif not self.fontSize == other.fontSize:
                return False
        except:
            return False
        
        for key, value in self.variations.items():
            if self.variations[key] != other.variations[key]:
                return False
            
        if self.rotate != other.rotate:
            return False
        
        if self.fill != other.fill:
            return False
        
        return True

    def mod(self, **kwargs):
        """Modify this style object to create a new
        one; kwargs can have all of the same kwargs as
        the standard `Style` constructor"""
        keyed = dict(**self.input, **self.input["kwargs"])
        del keyed["kwargs"]
        del keyed["self"]
        keyed.update(kwargs)
        return Style(**keyed)
    
    def print(self, *args):
        print(*args)
        return self
    
    def complete_metrics(self):
        c = False
        a = False
        d = False

        if self.capHeight is None and "c" in self.metrics:
            c = True
        elif self.ascender is None and "a" in self.metrics:
            a = True

        if self.descender is None and "d" in self.metrics:
            d = True    

        try:
            if "OS/2" in self.font.font.ttFont:
                os2 = self.font.font.ttFont["OS/2"]
                if c:
                    self.capHeight = os2.sCapHeight if hasattr(os2, "sCapHeight") else 0
                    if self.capHeight == 0:
                        self.capHeight = os2.sTypoAscender if hasattr(os2, "sTypoAscender") else 750
                if a:
                    self.ascender = os2.sTypoAscender if hasattr(os2, "sTypoAscender") else 0
                    if self.ascender == 0:
                        self.ascender = os2.sCapHeight if hasattr(os2, "sCapHeight") else 750
                if d:
                    self.descender = -os2.sTypoDescender if hasattr(os2, "sTypoDescender") else 250
            
            # TODO does this every happen?
            elif hasattr(self.font.font, "info"):
                if c:
                    self.capHeight = self.font.font.info.capHeight
                if a:
                    self.ascender = self.font.font.info.ascender
                if d:
                    self.descender = -self.font.font.info.descender
            
            # TODO also does this ever happen?
            elif hasattr(self.font.font, "defaultInfo"):
                if c:
                    self.capHeight = self.font.font.defaultInfo.capHeight
                if a:
                    self.ascender = self.font.font.defaultInfo.ascender
                if d:
                    self.descender = -self.font.font.defaultInfo.descender
        except AttributeError:
            pass
    
    def addVariations(self, variations, limits=dict()):
        for k, v in self.normalizeVariations(variations).items():
            self.variations[k] = v
        for k, v in self.normalizeVariations(limits).items():
            self.variationLimits[k] = v
    
    def normalizeVariations(self, variations):
        scale = self.scaleVariations
        roll = self.rollVariations

        for k, v in variations.items():
            try:
                axis = self.axes[k]
            except KeyError:
                continue

            if v == "min":
                variations[k] = axis.minValue
            elif v == "max":
                variations[k] = axis.maxValue
            elif v == "default":
                variations[k] = axis.defaultValue
            elif isinstance(v, str):
                coords = self.font.instances(scaled=False, search=v)
                if coords:
                    variations[k] = coords[axis.axisTag]
                else:
                    variations[k] = axis.defaultValue
            elif scale:
                vv = v
                if roll:
                    vv = v%2
                    if 1 < vv < 2:
                        vv = 2 - vv
                _v = max(0, min(1, vv))
                variations[k] = float(abs(axis.maxValue-axis.minValue)*_v + axis.minValue)
            else:
                if v < axis.minValue or v > axis.maxValue:
                    variations[k] = max(axis.minValue, min(axis.maxValue, v))
                    print("----------------------")
                    print("Invalid Font Variation")
                    print(self.font.path, self.axes[k].axisTag, v)
                    print("> setting", v, "<to>", variations[k])
                    print("----------------------")
                else:
                    variations[k] = v
        return variations
    
    def StretchX(flatten=10, debug=0, **kwargs):
        d = {}
        
        def stretcher(w, xp, i, p):
            np = (p.flatten(flatten) if flatten else p).nonlinear_transform(lambda x,y: (x if x < xp else x + w, y))
            if debug:
                (np.record(P()
                    .line([(xp, -250), (xp, 1000)])
                    .outline()))
            return np

        def is_left(a, b, c):
            return ((b[0] - a[0])*(c[1] - a[1]) - (b[1] - a[1])*(c[0] - a[0])) > 0
        
        def stretcher_slnt(w, xy, angle, i, p):
            if abs(angle) in [90, 270]:
                return p
            x0, y0 = xy
            ra = math.radians(90+angle)
            xdsc = x0 + (-250 - y0) / math.tan(ra)
            xasc = x0 + (1000 - y0) / math.tan(ra)

            np = (p.flatten(flatten) if flatten else p).nonlinear_transform(lambda x,y: (x if is_left((xdsc, -250), (xasc, 1000), (x, y)) else x + w, y))
            if debug:
                (np
                    .record(P()
                        .line([(xdsc, -250), (xasc, 1000)])
                        .outline())
                    .record(P()
                        .moveTo((x0+50/2, y0+50/2))
                        .dots(radius=50)))
            return np
        
        for k, v in kwargs.items():
            if len(v) == 3:
                d[k] = (v[0], partial(stretcher_slnt, v[0], v[1], v[2]))
            elif len(v) == 2:
                d[k] = (v[0], partial(stretcher, v[0], v[1]))
            elif len(v) == 1:
                pass
    
        return d
    
    def StretchY(flatten=10, align="mdy", debug=0, **kwargs):
        d = {}
        
        def stretcher(h, yp, i, p):
            np = (p.flatten(flatten) if flatten else p).nonlinear_transform(lambda x,y: (x, y if y < yp else y + h))
            if align == "mdy":
                np.translate(0, -h/2)
            elif align == "mxy":
                np.translate(0, -h)
            if debug:
                (np.record(P()
                    .line([(0, yp), (p.ambit().point("E").x, yp)])
                    .outline()))
            return np

        def is_left(a, b, c):
            return ((b[0] - a[0])*(c[1] - a[1]) - (b[1] - a[1])*(c[0] - a[0])) > 0
        
        def stretcher_slnt(h, xy, angle, i, p):
            if abs(angle) in [90, 270]:
                return p
            x0, y0 = xy
            ra = math.radians(90+angle)
            ydsc = y0 + (0 - x0) / math.tan(ra)
            yasc = y0 + (p.ambit().point("E").x - x0) / math.tan(ra)
            p0 = (0, ydsc)
            p1 = (p.ambit().point("E").x, yasc)

            np = (p.flatten(flatten) if flatten else p).nonlinear_transform(lambda x,y: (x, y if not is_left(p0, p1, (x, y)) else y + h))
            if debug:
                (np
                    .record(P()
                        .line([p0, p1])
                        .outline())
                    .record(P()
                        .moveTo((x0+50/2, y0+50/2))
                        .dots(radius=50)))
            return np
        
        for k, v in kwargs.items():
            if len(v) == 3:
                d[k] = (0, partial(stretcher_slnt, v[0], v[1], v[2]))
            elif len(v) == 2:
                d[k] = (0, partial(stretcher, v[0], v[1]))
            elif len(v) == 1:
                pass
        return d


def offset(x, y, ox, oy):
    return (x + ox, y + oy)


class StyledString(FittableMixin):
    """
    Lowest-level vectorized typesetting class
    """
    def __init__(self, text:str, style:Style):
        if style.case is not None:
            if style.case == "upper":
                text = text.upper()
            elif style.case == "lower":
                text = text.lower()
        
        self.text_info = TextInfo(text)
        self.text = text
        self.setStyle(style)
        if self.style.lang:
            self.text_info.languageOverride = self.style.lang
        self.resetGlyphRun()
    
    def setStyle(self, style):
        self.style = style
        # these will change based on fitting, so we make copies
        self.fontSize = self.style.fontSize
        self.tracking = self.style.tracking
        self.features = self.style.features.copy()
        self.variations = self.style.variations.copy()
    
    def resetGlyphRun(self):
        #print("RESET GLYPH RUN", self)
        self.glyphs = self.style.font.font.getGlyphRunFromTextInfo(self.text_info
            , features=self.features
            , varLocation=self.variations
            )
        #self.glyphs = self.style.font.font.getGlyphRun(self.text, features=self.features, varLocation=self.variations)
        x = 0
        for glyph in self.glyphs:
            #print(">>>>", glyph.gid)

            glyph.frame = Rect(x+glyph.dx, glyph.dy, glyph.ax, self.style._asc)
            if "d" in self.style.metrics:
                glyph.frame = glyph.frame.expand(self.style.descender, "N")
            x += glyph.ax
        
        #print("resetGlyphRun")
        self.getGlyphFrames()
    
    def trackFrames(self, space_width=0):
        t = self.tracking
        x_off = 0
        for idx, g in enumerate(self.glyphs):
            g.frame = g.frame.offset(x_off, 0)
            x_off += t
            
            if self.style.mods:
                mod_data = self.style.mods.get(g.name, self.style.mods.get("_wildcard"))
                if mod_data is not None:
                    x_off += mod_data[0]
            
            if self.style.space and g.name.lower() == "space":
                x_off += (self.style.space - space_width)
    
    def adjustFramesForPath(self):
        for idx, g in enumerate(self.glyphs):    
            if self.style.xShift:
                try:
                    g.frame.x += self.style.xShift[idx]
                except:
                    g.frame.x += self.style.xShift
                    pass
    
    def getGlyphFrames(self):
        if self.style.kern_pairs:
            last_gn = None
            for idx, glyph in enumerate(self.glyphs):
                gn = glyph.name

                for chars, kp in self.style.kern_pairs.items():
                    try:
                        l = kp[0]
                        adv = kp[1]
                    except TypeError:
                        l = kp
                        adv = 0
                    if isinstance(chars, str):
                        a, b = chars.split("/")
                    else:
                        a, b = chars
                    if gn == b and last_gn == a:
                        kern_shift = l
                        if kern_shift != 0:
                            for glyph in self.glyphs[idx:]:
                                glyph.frame.x += kern_shift
                last_gn = gn
        
        space_width = 0
        for glyph in self.glyphs:
            if glyph.name == "space" and self.style.space and self.style.space > 0:
                space_width = glyph.frame.w
                glyph.frame.w = self.style.space

        if self.style.trackingMode == 1:
            self.trackFrames(space_width=space_width)

        for glyph in self.glyphs:
            glyph.frame = glyph.frame.scale(self.scale())

        if self.style.trackingMode == 0:
            self.trackFrames()

        self.adjustFramesForPath()
    
    def scale(self):
        return self.fontSize / self.style.font.font.shaper.face.upem
    
    def width(self): # size?
        try:
            w = self.glyphs[-1].frame.point("SE").x # TODO need to scale?
        except IndexError:
            return 0
        #return w * self.scale()
        return w
        return self.getGlyphFrames()[-1].frame.point("SE").x
    
    def height(self):
        asc = self.style._asc * self.scale()
        if "d" in self.style.metrics:
            asc += self.style.descender * self.scale()
        return asc
    
    def textContent(self):
        return self.text
    
    def fitField(self, field, value):
        if field == "tracking":
            self.tracking = value
        elif field == "wdth":
            self.variations["wdth"] = value
        elif field == "fontSize":
            self.fontSize = value
    
    def binaryFit(self, width, field, minv, maxv, tries):
        midv = (maxv-minv)*0.5+minv
        self.fitField(field, maxv)
        self.resetGlyphRun()
        maxw = self.width()
        self.fitField(field, midv)
        self.resetGlyphRun()
        midw = self.width()
        self.fitField(field, minv)
        self.resetGlyphRun()
        minw = self.width()
        if abs(maxw - midw) < 0.5:
            #print(self.text, ">>>", tries)
            return
        if width > midw:
            self.binaryFit(width, field, midv, maxv, tries+1)
        else:
            self.binaryFit(width, field, minv, midv, tries+1)
        #return super().fit(width)
    
    def testWidth(self, width, field, minv, maxv):
        self.resetGlyphRun()
        w = self.width()
        if w == width:
            print("VERY RARE")
            return True
        elif w < width: # too small, which means we know it'll fit based on this property
            self.binaryFit(width, field, minv, maxv, 0)
            return True
        else: # too big, so we maintain current value & let the caller know
            return False
    
    def _fit(self, width):
        if isinstance(width, Rect):
            width = width.w

        continuing = True
        failed = False

        if self.style.tracking > 0:
            self.tracking = 0
            if self.testWidth(width, "tracking", 0, self.style.tracking):
                continuing = False
        if continuing:
            minwdth = self.style.variationLimits.get("wdth", 1)
            currentwdth = self.style.variations.get("wdth", 1)
            self.variations["wdth"] = minwdth
            if not self.testWidth(width, "wdth", minwdth, currentwdth):
                #self.tracking = self.style.trackingLimit
                if not self.testWidth(width, "tracking", self.style.trackingLimit, min(self.style.tracking, 0)):
                    if self.style.varyFontSize:
                        self.fontSize = 10
                        if not self.testWidth(width, "fontSize", 10, self.style.fontSize):
                            self.variations["wdth"] = minwdth
                            failed = True
                    else:
                        self.variations["wdth"] = minwdth
                        failed = True
        if failed:
            print("FAILED TO FIT >>>", self.text, self.width(), width)
        return self

    def shrink(self):
        #print(self.text, self.variations)
        adjusted = False
        default_step = 1
        if self.tracking > 0 and self.tracking > self.style.trackingLimit:
            self.tracking -= self.style.increments.get("tracking", default_step)
            adjusted = True
        else:
            for k, v in self.style.variationLimits.items():
                if self.variations[k] > self.style.variationLimits[k]:
                    self.variations[k] -= self.style.increments.get(k, default_step)
                    adjusted = True
                    break
        if not adjusted and self.tracking > self.style.trackingLimit:
            self.tracking -= self.style.increments.get("tracking", default_step)
            adjusted = True
        if not adjusted and self.style.varyFontSize:
            self.fontSize -= 1
            self.tracking = self.style.tracking
            adjusted = True
        if not adjusted and self.style.narrower:
            self.setStyle(self.style.narrower)
            adjusted = True
        if not adjusted and self.style.preventHwid == False and "hwid" not in self.features:
            self.features["hwid"] = True
            self.tracking = self.style.tracking # reset to widest
            self.resetGlyphRun()
            #self.glyphs = self.hb.glyphs(self.variations, self.features)
            adjusted = True
        self.resetGlyphRun()
        return adjusted
    
    def scalePenToStyle(self, glyph, in_pen, idx):
        s = self.scale()
        t = Transform()
        try:
            bs = self.style.baselineShift[idx]
        except:
            bs = self.style.baselineShift
        
        if callable(bs):
            t = t.translate(0, bs(idx))
        else:
            try:
                t = t.translate(0, bs[idx])
            except:
                try:
                    t = t.translate(0, bs)
                except:
                    pass
        
        t = t.scale(s)
        s = self.scale()
        if s > 0:
            t = t.translate(glyph.frame.x/s, glyph.frame.y/s)

        out_pen = P()
        tp = TransformPen(out_pen, (t[0], t[1], t[2], t[3], t[4], t[5]))
        ip = P().record(in_pen)
        if self.style.mods:
            mod_data = self.style.mods.get(glyph.name)
            if mod_data is None and "_wildcard" in self.style.mods:
                mod_data = self.style.mods["_wildcard"]
            if mod_data is not None:
                w, mod = mod_data
                mod(-1, ip)
        ip.replay(tp)
        if self.style.rotate:
            out_pen.rotate(self.style.rotate)
        
        # TODO this shouldn't be necessary
        # if True:
        #     valid_values = []
        #     for (move, pts) in out_pen.value:
        #         if move != "addComponent":
        #             valid_values.append((move, pts))
        #     out_pen.value = valid_values

        return out_pen
    
    def _emptyPenWithAttrs(self):
        #attrs = dict(fill=self.style.fill)
        #if self.style.stroke:
        #    attrs["stroke"] = dict(color=self.style.stroke, weight=self.style.strokeWidth)
        dp = P().f(self.style.fill)
        if self.style.stroke:
            dp.s(self.style.stroke).sw(self.style.strokeWidth)
        return dp
    
    def buildLayeredGlyph(self, idx, glyph, output, layer, frame):
        layerGlyph = P().record(layer)
        if layerGlyph.v.value:
            output.append(layerGlyph)
        
        layerGlyph.data(glyphName=f"{glyph.name}_layer_{idx}")

        #print(">>>>>>>>>>>>", layer.method)

        if layer.method == "drawPathSolid":
            layerGlyph.f(layer.data["color"])
        else:
            gradientGlyph = P()
            if layer.method == "drawPathLinearGradient":
                (gradientGlyph
                    .line([layer.data["pt1"], layer.data["pt2"]])
                    .fssw(-1, 0, 2)
                    #.translate(frame.x, 0)
                    )
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
    
    def addBRGlyphDrawings(self, glyphs):
        ax = 0
        surface = BRPathCollectorSurface()

        self.style.font._brFont.setLocation(self.variations)

        if self.style.palette:
            p = self.style.palette
            if isinstance(p, int):
                palette = self.style.font._brFont.getPalette(p)
            else:
                palette = p
        else:
            palette = None

        with surface.canvas((0, 0, 1000, 1000)) as canvas:
            for glyph in glyphs:
                frame = Rect(
                    ax + glyph.dx,
                    glyph.dy,
                    glyph.ax,
                    self.style._asc) # how does ay play in?
                
                output = P().data(glyphName=glyph.name, frame=frame)

                with canvas.savedState():
                    #canvas.translate(glyph.dx, glyph.dy)

                    self.style.font._brFont.drawGlyph(glyph.name, canvas, palette=palette)

                    layers = canvas.paths

                    if isinstance(layers, BRPathCollectorRecordingPen):
                        if layers.method == "drawPathSolid": # trad font
                            output.record(layers).f(layers.data["color"])
                            layers = None
                        else:
                            layers = [layers]
                    
                    if layers:
                        for idx, layer in enumerate(layers):
                            self.buildLayeredGlyph(idx, glyph, output, layer, frame)
                    
                    canvas.paths = []

                #canvas.translate(glyph.ax, glyph.ay)

                glyph.glyphDrawing = output
                #ax += glyph.ax

    def pens(self) -> P:
        """
        Vectorize text into a `P`, such that each glyph (or ligature) is represented by a single `P` (or a `P` in the case of a color font, which will then nest a `P` for each layer of that color glyph)
        """

        # Guess this has been here for years but it seems to be redundant?
        #self.resetGlyphRun()

        colrv1 = self.style.font._colrv1
        brFont = self.style.font._brFont

        if brFont:
            self.addBRGlyphDrawings(self.glyphs)

        elif not self.style.no_shapes:
            #print("ct.getGlyphDrawings")
            glyphNames = [g.name for g in self.glyphs]
            glyphDrawings = list(self.style.font.font.getGlyphDrawings(glyphNames, True))
            for glyph, glyphDrawing in zip(self.glyphs, glyphDrawings):
                glyph.glyphDrawing = glyphDrawing
        
        pens = P()
        for idx, g in enumerate(self.glyphs):

            # TODO this is sketchy but seems to correct
            # some line-spacing issues with arabic?
            norm_frame = g.frame
            norm_frame = Rect(g.frame.x, 0, g.frame.w, self.style._asc*self.scale())

            dp_atom = self._emptyPenWithAttrs()
            if self.style.no_shapes:
                if callable(self.style.show_frames):
                    dp_atom.record(P().rect(self.style.show_frames(g.frame)).outline(4))
                else:
                    dp_atom.record(P().rect(g.frame).outline(1 if self.style.show_frames is True else self.style.show_frames))
                
                dp_atom.data(
                    frame=norm_frame,
                    glyphName=g.name,
                    glyphCluster=g.cluster,
                    #glyphID=g.gid,
                )
                # dp_atom.typographic = True
                # dp_atom.addFrame(norm_frame)
                # dp_atom.glyphName = g.name
            
            elif not brFont and isinstance(g.glyphDrawing, GlyphDrawing):
                dp_atom.v.value = self.scalePenToStyle(g, g.glyphDrawing.path, idx).v.value
                
                if "d" in self.style.metrics:
                    dp_atom.translate(0, self.style.descender*self.scale())
                
                dp_atom.data(
                    frame=norm_frame,
                    glyphName=g.name,
                    glyphCluster=g.cluster,
                    #glyphID=g.gid,
                )

                if self.style.show_frames:
                    if callable(self.style.show_frames):
                        #dp_atom.record(P().rect(self.style.show_frames(g.frame)).outline(4))
                        dp_atom.rect(self.style.show_frames(g.frame))
                    else:
                        dp_atom.record(P().rect(g.frame).outline(1 if self.style.show_frames is True else self.style.show_frames))
                        #dp_atom.rect(g.frame)
                if self.style.q2c:
                    dp_atom.q2c()
                if self.style.removeOverlap:
                    dp_atom.removeOverlap()

            elif brFont:
                dp_atom = g.glyphDrawing
                dp_atom.layered = len(dp_atom) > 1 or colrv1

                for idx, layer in enumerate(dp_atom):
                    layer.v.value = self.scalePenToStyle(g, layer, idx).v.value

                    ss = layer.data("substructure")
                    if ss:
                        ss.v.value = self.scalePenToStyle(g, ss, idx).v.value
                
                if not dp_atom.layered:
                    dp_atom = dp_atom[0]
                
                dp_atom.data(
                   frame=norm_frame,
                   glyphName=g.name)

                if self.style.q2c:
                    dp_atom.q2c()
                if self.style.removeOverlap:
                    dp_atom.removeOverlap()
                
            else:
                print("HERE!")
                # dp_atom = P()
                # dp_atom.layered = True
                # for lidx, layer in enumerate(g.glyphDrawing.layers):
                #     dp_layer = self._emptyPenWithAttrs()
                #     #dp_layer.value = layer[0].value
                #     dp_layer.v.value = self.scalePenToStyle(g, layer[0], idx).v.value
                #     if isinstance(self.style.palette, int):
                #         dp_layer.f(self.style.font.font.colorPalettes[self.style.palette][layer[1]])
                #     else:
                #         dp_layer.f(self.style.palette[layer[1]])
                #     if len(dp_layer.v.value) > 0:
                #         #dp_layer.addFrame(g.frame, typographic=True)
                #         dp_layer.data(glyphName=f"{g.name}_layer_{lidx}")
                #         #dp_layer.glyphName = 
                #         dp_atom += dp_layer
                
                # dp_atom.data(
                #     frame=norm_frame,
                #     glyphName=g.name
                # )
                
                # dp_atom.addFrame(norm_frame, typographic=True)
                # dp_atom.glyphName = g.name
            
            #dp_atom._parent = pens
            if self.style.meta:
                dp_atom.data(**self.style.meta)
            
            pens.append(dp_atom)
        
        if self.style.cluster:
            def cluster(p:P):
                first = p[0]
                glyphName = "+".join([x.data("glyphName") for x in p])
                for r in p[1:]:
                    first.record(r)
                return first.data(glyphName=glyphName)

            pens = (pens
                .partition(lambda p: p.data("glyphCluster"))
                .map(cluster))
        
        if self.style.postTracking != 0:
            #print(self.style.postTracking * self.style.fontSize/1000)
            pens.track(self.style.postTracking * self.style.fontSize/1000)

        if self.style.reverse:
            pens.reversePens()

        pens.data(**self.style.data)

        ro = pens
        if self.style.annotate:
            ro._stst = self
        return ro

    def pen(self, frame=True) -> P:
        """
        Vectorize all text into single `P`
        """
        return self.pens().pen()
    
    def instance(self, output_path, remove_overlaps=False, freeze=False, freeze_suffix=None):
        args = ["fonttools", "varLib.instancer", self.style.font.path.absolute()]
        
        for k,v in self.variations.items():
            args.append(f"{k}={v}")
        
        args.extend(["-o", output_path])
        
        if remove_overlaps:
            args.append("--remove-overlaps")
        
        run_with_check(args)

        if freeze:
            enabled_features = []
            for k,v in self.features.items():
                if v:
                    enabled_features.append(k)
            
            features = ",".join(enabled_features)
            args = ["pyftfeatfreeze", "-f", features]
            if freeze_suffix:
                args.extend(["-S", "-U", freeze_suffix])
            
            args.append(output_path)
            run_with_check(args)
            
            frozen_otf = Path(str(output_path) + ".featfreeze.otf")
            copy2(frozen_otf, output_path)
            frozen_otf.unlink()
        
        return Font(str(output_path))

class SegmentedString(FittableMixin):
    def __init__(self, text, styles):
        self.text_info = TextInfo(text)
        self.strings = []
        self.segment_data = []
        for segmentText, segmentScript, segmentBiDiLevel, firstCluster in self.text_info._segments:
            self.strings.append(StyledString(segmentText, styles[segmentScript]))
            cluster_data = []
            for index, char in enumerate(segmentText, firstCluster):
                cluster_data.append(
                    dict(index=index, char=char, unicode=f"U+{ord(char):04X}",
                        unicodeName=unicodedata.name(char, "?"), script=segmentScript,
                        bidiLevel=segmentBiDiLevel, dir=["LTR", "RTL"][segmentBiDiLevel % 2])
                )
            self.segment_data.append(cluster_data)
    
    def width(self):
        return sum([s.width() for s in self.strings])
    
    def height(self):
        return max([s.height() for s in self.strings])
    
    def textContent(self):
        return "-".join([s.textContent() for s in self.strings])

    def shrink(self):
        adjusted = False
        for s in self.strings:
            adjusted = s.shrink() or adjusted
        return adjusted

    def pens(self, flat=True):
        pens = P()
        x_off = 0
        for s in self.strings:
            dps = s.pens()
            #if dps.layered:
            #    pens.layered = True
            dps.translate(x_off, 0)
            if flat:
                pens.extend(dps._els)
            else:
                if s.style.lang:
                    dps.data(lang=s.style.lang)
                pens.append(dps)
            x_off += dps.ambit().w
        return pens