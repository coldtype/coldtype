from pathlib import Path
from collections import OrderedDict
from functools import partial

import unicodedata, os, math

from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.pens.boundsPen import ControlBoundsPen, BoundsPen
from fontTools.ttLib.ttFont import TTFont

from coldtype.color import normalize_color
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.geometry import Rect, Point

try:
    from fontgoggles.font import getOpener
    from fontgoggles.font.baseFont import BaseFont
    from fontgoggles.font.otfFont import OTFFont
    from fontgoggles.misc.textInfo import TextInfo
except ModuleNotFoundError:
    from coldtype.fontgoggles.font import getOpener
    from coldtype.fontgoggles.font.baseFont import BaseFont
    from coldtype.fontgoggles.font.otfFont import OTFFont
    from coldtype.fontgoggles.misc.textInfo import TextInfo


class FittableMixin():
    def textContent(self):
        print("textContent() not overwritten")

    def fit(self, width):
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


_prefixes = [
    ["¬", "~/Library/Fonts"],
    ["", "/Library/Fonts"]
]

class FontNotFoundException(Exception):
    pass

def normalize_font_prefix(path_string):
    for prefix, expansion in _prefixes:
        path_string = path_string.replace(prefix, expansion)
    return Path(path_string).expanduser().resolve()

def normalize_font_path(font):
    global _prefixes
    literal = normalize_font_prefix(str(font))
    ufo = literal.suffix == ".ufo"
    if literal.exists() and (not literal.is_dir() or ufo):
        return str(literal)
    else:
        raise FontNotFoundException(literal)

def empty_writer(*args):
    pass

class Font():
    # TODO support glyphs?
    def __init__(self, path, number=0):
        #ufo = glyphsLib.load_to_ufos(self.fontFile)[0]
        self.path = Path(normalize_font_path(path))
        numFonts, opener, getSortInfo = getOpener(self.path)
        self.font:BaseFont = opener(self.path, number)
        self.font.cocoa = False
    
    async def load(self):
        await self.font.load(empty_writer)
        #print(">>> loaded", self.path.name)
    
    async def Preload(path):
        font = Font(path)
        await font.load()
        return font

class Style():
    def RegisterShorthandPrefix(prefix, expansion):
        global _prefixes
        _prefixes.append([prefix, str(expansion)])

    def __init__(self,
            font=None,
            fontSize=12,
            fitHeight=None,
            tracking=0,
            trackingLimit=0,
            trackingMode=1,
            kern_pairs=dict(),
            overlap_pairs=dict(),
            overlap_outline=3,
            space=None,
            baselineShift=0,
            xShift=None,
            mods=None,
            variations=dict(),
            variationLimits=dict(),
            increments=dict(),
            features=dict(),
            liga=True,
            varyFontSize=False,
            fill=(0, 0.5, 1),
            stroke=None,
            strokeWidth=0,
            palette=0,
            capHeight=None,
            data={},
            latin=None, # temp
            lang=None,
            filter=None,
            layerer=None,
            preventHwid=False,
            layer=None,
            reverse=False,
            removeOverlap=False,
            rotate=0,
            sv=True,
            narrower=None,
            **kwargs):
        """
        kern_pairs (kp) — a dict of glyphName->[left,right] values in font-space
        tracking (t)
        trackingLimit (tl)
        baselineShift (bs)
        capHeight (ch) — A number in font-space; not specified, read from font; specified as 'x', capHeight is set to xHeight as read from font
        """

        self.input = locals()
        self.input["self"] = None

        if isinstance(font, str):
            self.font:Font = Font(font)
            if isinstance(self.font.font, OTFFont):
                self.font.font._syncLoad(None)
            else:
                print("Editable font formats cannot be loaded synchronously")

        else:
            self.font:Font = font

        self.narrower = narrower
        self.layer = layer
        self.layerer = layerer
        self.reverse = kwargs.get("r", reverse)
        self.removeOverlap = kwargs.get("ro", removeOverlap)
        self.rotate = rotate
        self.sv = sv # scale-variations
        
        if "OS/2" in self.font.font.ttFont:
            os2 = self.font.font.ttFont["OS/2"]
            self.capHeight = os2.sCapHeight if hasattr(os2, "sCapHeight") else 0
            if self.capHeight == 0:
                self.capHeight = os2.sTypoAscender if hasattr(os2, "sTypoAscender") else 750
        elif hasattr(self.font.font, "info"):
            self.capHeight = self.font.font.info.capHeight
        elif hasattr(self.font.font, "defaultInfo"):
            self.capHeight = self.font.font.defaultInfo.capHeight

        if capHeight: # override whatever the font says
            if capHeight != "x":
                self.capHeight = capHeight

        if fitHeight:
            self.fontSize = (fitHeight/self.capHeight)*1000
        else:
            self.fontSize = fontSize

        self.tracking = kwargs.get("t", tracking)
        self.kern_pairs = kwargs.get("kp", kern_pairs)
        self.overlap_pairs = overlap_pairs
        self.overlap_outline = overlap_outline
        self.trackingMode = trackingMode
        self.trackingLimit = kwargs.get("tl", trackingLimit)
        self.baselineShift = kwargs.get("bs", baselineShift)
        self.increments = increments
        self.space = space
        self.xShift = kwargs.get("xs", xShift)
        self.mods = mods
        self.palette = palette
        self.lang = lang
        self.filter = filter
        self.data = data
        self.latin = latin
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
            if k in ["dlig", "swsh", "onum", "tnum", "palt", "salt"]:
                found_features[k] = v
            if k in ["slig"]:
                if k == 0:
                    found_features[k] = 0
        
        self.features = {**dict(kern=True, liga=liga), **found_features}

        self.fill = normalize_color(fill)
        self.stroke = normalize_color(stroke)
        if stroke and strokeWidth == 0:
            self.strokeWidth = 1
        else:
            self.strokeWidth = strokeWidth

        unnormalized_variations = variations.copy()
        self.axes = OrderedDict()
        self.variations = dict()
        self.variationLimits = dict()
        self.varyFontSize = varyFontSize
        
        if self.font.font.ttFont:
            try:
                fvar = self.font.font.ttFont['fvar']
            except:
                fvar = None
            if fvar:
                for axis in fvar.axes:
                    self.axes[axis.axisTag] = axis
                    self.variations[axis.axisTag] = axis.defaultValue
                    if axis.axisTag == "wdth": # the only reasonable default
                        self.variationLimits[axis.axisTag] = axis.minValue
                    if axis.axisTag in kwargs and axis.axisTag not in variations:
                        unnormalized_variations[axis.axisTag] = kwargs[axis.axisTag]

            self.addVariations(unnormalized_variations)
    
    def __eq__(self, other):
        if not self.font == other.font:
            return False
        elif not self.fontSize == other.fontSize:
            return False
        
        for key, value in self.variations.items():
            if self.variations[key] != other.variations[key]:
                return False
        
        if self.fill != other.fill:
            return False
        
        return True

    def mod(self, **kwargs):
        keyed = dict(**self.input, **self.input["kwargs"])
        del keyed["kwargs"]
        del keyed["self"]
        keyed.update(kwargs)
        return Style(**keyed)
    
    def addVariations(self, variations, limits=dict()):
        for k, v in self.normalizeVariations(variations).items():
            self.variations[k] = v
        for k, v in self.normalizeVariations(limits).items():
            self.variationLimits[k] = v
    
    def normalizeVariations(self, variations):
        scale = self.sv
        for k, v in variations.items():
            try:
                axis = self.axes[k]
            except KeyError:
                #print("Invalid axis", self.fontFile, k)
                continue
                #raise Exception("Invalid axis", self.fontFile, k)
            if v == "min":
                variations[k] = axis.minValue
            elif v == "max":
                variations[k] = axis.maxValue
            elif v == "default":
                variations[k] = axis.defaultValue
            elif scale and v <= 1.0:
                variations[k] = float(abs(axis.maxValue-axis.minValue)*v + axis.minValue)
            else:
                if v < axis.minValue or v > axis.maxValue:
                    variations[k] = max(axis.minValue, min(axis.maxValue, v))
                    print("----------------------")
                    print("Invalid Font Variation")
                    print(self.fontFile, self.axes[k].axisTag, v)
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
                (np.record(DATPen()
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
                    .record(DATPen()
                        .line([(xdsc, -250), (xasc, 1000)])
                        .outline())
                    .record(DATPen()
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
                (np.record(DATPen()
                    .line([(0, yp), (p.getFrame().point("E").x, yp)])
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
            yasc = y0 + (p.getFrame().point("E").x - x0) / math.tan(ra)
            p0 = (0, ydsc)
            p1 = (p.getFrame().point("E").x, yasc)

            np = (p.flatten(flatten) if flatten else p).nonlinear_transform(lambda x,y: (x, y if not is_left(p0, p1, (x, y)) else y + h))
            if debug:
                (np
                    .record(DATPen()
                        .line([p0, p1])
                        .outline())
                    .record(DATPen()
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
    def __init__(self, text, style):
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
        self.glyphs = self.style.font.font.getGlyphRunFromTextInfo(self.text_info, addDrawings=False, features=self.features, varLocation=self.variations)
        #self.glyphs = self.style.font.font.getGlyphRun(self.text, features=self.features, varLocation=self.variations)
        x = 0
        for glyph in self.glyphs:
            glyph.frame = Rect(x+glyph.dx, glyph.dy, glyph.ax, self.style.capHeight)
            x += glyph.ax
        self.getGlyphFrames()
    
    def trackFrames(self):
        t = self.tracking
        x_off = 0
        for idx, g in enumerate(self.glyphs):
            g.frame = g.frame.offset(x_off, 0)
            x_off += t
            if self.style.mods and g.name in self.style.mods:
                x_off += self.style.mods[g.name][0]
            if self.style.space and g.name.lower() == "space":
                x_off += self.style.space
    
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
        
        if self.style.trackingMode == 1:
            self.trackFrames()

        for glyph in self.glyphs:
            glyph.frame = glyph.frame.scale(self.scale())

        if self.style.trackingMode == 0:
            self.trackFrames()

        self.adjustFramesForPath()
    
    def scale(self):
        return self.fontSize / self.style.font.font.shaper.face.upem
    
    def width(self): # size?
        w = self.glyphs[-1].frame.point("SE").x # TODO need to scale?
        #return w * self.scale()
        return w
        return self.getGlyphFrames()[-1].frame.point("SE").x
    
    def height(self):
        return self.style.capHeight*self.scale()
    
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
    
    def scalePenToStyle(self, glyph, in_pen):
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
        t = t.translate(glyph.frame.x/self.scale(), glyph.frame.y/self.scale())
        #t = t.translate(0, bs)
        out_pen = DATPen()
        tp = TransformPen(out_pen, (t[0], t[1], t[2], t[3], t[4], t[5]))
        ip = DATPen().record(in_pen)
        if self.style.mods and glyph.name in self.style.mods:
            w, mod = self.style.mods[glyph.name]
            mod(-1, ip)
        ip.replay(tp)
        if self.style.rotate:
            out_pen.rotate(self.style.rotate)
        
        # TODO this shouldn't be necessary
        if True:
            valid_values = []
            for (move, pts) in out_pen.value:
                if move != "addComponent":
                    valid_values.append((move, pts))
            out_pen.value = valid_values

        return out_pen
    
    def _emptyPenWithAttrs(self):
        attrs = dict(fill=self.style.fill)
        if self.style.stroke:
            attrs["stroke"] = dict(color=self.style.stroke, weight=self.style.strokeWidth)
        dp = DATPen(**attrs)
        return dp

    def pens(self, frame=True) -> DATPenSet:
        self.resetGlyphRun()
        self.style.font.font.addGlyphDrawings(self.glyphs, colorLayers=True)
        
        pens = DATPenSet()
        for idx, g in enumerate(self.glyphs):
            dp_atom = self._emptyPenWithAttrs()
            if len(g.glyphDrawing.layers) == 1:
                dp_atom.value = self.scalePenToStyle(g, g.glyphDrawing.layers[0][0]).value
                dp_atom.typographic = True
                dp_atom.addFrame(g.frame)
                dp_atom.glyphName = g.name
                if self.style.removeOverlap:
                    dp_atom.removeOverlap()
            else:
                dp_atom = DATPenSet()
                dp_atom.layered = True
                for layer in g.glyphDrawing.layers:
                    dp_layer = self._emptyPenWithAttrs()
                    #dp_layer.value = layer[0].value
                    dp_layer.value = self.scalePenToStyle(g, layer[0]).value
                    dp_layer.f(self.style.font.font.colorPalettes[self.style.palette][layer[1]])
                    dp_atom += dp_layer
                dp_atom.addFrame(g.frame, typographic=True)
                dp_atom.glyphName = g.name
            pens.append(dp_atom)

        if self.style.reverse:
            pens.reversePens()
        
        if self.style.kern_pairs:
            overlap_pairs = {pair:value[2] for (pair, value) in self.style.kern_pairs.items() if not isinstance(value, int) and len(value) > 2}
            pens.overlapPairs(overlap_pairs, outline=self.style.overlap_outline)
        return pens

    def pen(self, frame=True) -> DATPen:
        return self.pens(frame=frame).pen()

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

    def pens(self):
        pens = DATPenSet()
        x_off = 0
        for s in self.strings:
            dps = s.pens(frame=True)
            if dps.layered:
                pens.layered = True
            dps.translate(x_off, 0)
            pens.extend(dps.pens)
            x_off += dps.getFrame().w
        return pens
        #return DATPenSet([s.pens(frame=True) for s in self.strings])