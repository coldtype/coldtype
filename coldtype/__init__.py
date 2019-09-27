import math
import sys
import os
import re
import copy

name = "coldtype"
dirname = os.path.dirname(__file__)

from collections import OrderedDict
import freetype
from freetype.raw import *
from fontTools.ttLib.tables import otTables
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.pens.boundsPen import ControlBoundsPen, BoundsPen
from fontTools.ufoLib import UFOReader
from fontTools.ttLib import TTFont
import unicodedata
import uharfbuzz as hb
from itertools import groupby
from pprint import pprint

if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath(dirname + "/.."))

from coldtype.beziers import CurveCutter, raise_quadratic
from coldtype.color import normalize_color
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.geometry import Rect, Point
from coldtype.shaper import segment

try:
    # relies on undeclared dependencies
    from defcon import Font
    import glyphsLib
    from coldtype.pens import OutlinePen
except:
    pass

try:
    from booleanOperations.booleanGlyph import BooleanGlyph
    import drawBot as _drawBot
except:
    _drawBot = None


_FONT_CACHE = dict()


def get_cached_font(font_path):
    if font_path not in _FONT_CACHE:
        with open(font_path, 'rb') as fontfile:
            _FONT_CACHE[font_path] = fontfile.read()
    return _FONT_CACHE[font_path]


class HarfbuzzFrame():
    def __init__(self, gid, info, position, frame, glyphName):
        self.gid = gid #info.codepoint
        self.info = info
        self.position = position
        self.frame = frame
        self.glyphName = glyphName

    def __repr__(self):
        return f"HarfbuzzFrame: gid{self.gid}@{self.frame}"


class Harfbuzz():
    def __init__(self,
                 fontdata,
                 text="",
                 height=1000,
                 lang=None,
                 ttfont=None,
                 kern=dict()):
        self.face = hb.Face(fontdata)
        self.ttfont = ttfont
        self.kern = kern
        self.lang = lang
        self.height = height
        self.text = text
    
    def buffer(self, axes=dict(), features=dict()):
        font = hb.Font(self.face)
        font.scale = (self.face.upem, self.face.upem)
        hb.ot_font_set_funcs(font) # necessary?
        if len(axes.items()) > 0:
            font.set_variations(axes)
        
        buf = hb.Buffer()
        if self.lang:
            buf.language = self.lang
        buf.add_str(self.text)
        buf.guess_segment_properties()
        hb.shape(font, buf, features)
        return buf
    
    def glyphs(self, axes=dict(), features=dict()):
        buf = self.buffer(axes, features)
        glyphs = []
        for info in buf.glyph_infos:
            gid = info.codepoint
            cluster = info.cluster
            gn = self.ttfont.getGlyphName(gid) if self.ttfont else None
            code = gn.replace("uni", "")
            try:
                glyph_name = unicodedata.name(chr(int(code, 16)))
            except:
                glyph_name = code
            glyphs.append([gid, glyph_name])
        return glyphs
    
    def frames(self, axes=dict(), features=dict(), glyphs=[]):
        buf = self.buffer(axes, features)
        infos = buf.glyph_infos
        positions = buf.glyph_positions
        frames = []
        x = 0
        for idx, (info, pos) in enumerate(zip(infos, positions)):
            gid = info.codepoint
            #if gid != glyphs[idx][0]:
            #    print(">>>>>>>>", self.text)
            #    print(gid, glyphs[idx][0])
            #    #raise Exception("HELLO WORLD")
            cluster = info.cluster
            x_advance = pos.x_advance
            x_offset = pos.x_offset
            y_offset = pos.y_offset
            gn = glyphs[idx][1]
            if gn in self.kern:
                l, r = self.kern.get(gn)
                x_offset += l
                x_advance += r
            frames.append(HarfbuzzFrame(gid, info, pos, Rect(x+x_offset, y_offset, x_advance, self.height), gn)) # 100?
            x += x_advance
        return frames


class FontShapeReader():
    def __init__(self, style):
        self.style = style

    def setVariations(self, axes):
        pass
    
    def drawOutlineToPen(self, glyph_id, pen):
        pass


class UFOShapeReader(FontShapeReader):
    def drawOutlineToPen(self, glyph_id, pen):
        #print("drawing", glyph_id)
        self.style.glyphSet[glyph_id].draw(pen)


class FreetypeReader(FontShapeReader):
    def __init__(self, style):
        super().__init__(style)
        self.font = freetype.Face(style.fontFile)
        self.font.set_char_size(1000) # configurable?
        try:
            self.axesOrder = [a.axisTag for a in style.ttfont['fvar'].axes]
        except:
            self.axesOrder = []
    
    def setVariations(self, axes=dict()):
        if len(self.axesOrder) > 0:
            coords = []
            for name in self.axesOrder:
                #coord = FT_Fixed(int(axes[name]) << 16)
                coord = FT_Fixed(int(axes[name] * (2**16)))
                coords.append(coord)
            ft_coords = (FT_Fixed * len(coords))(*coords)
            freetype.FT_Set_Var_Design_Coordinates(self.font._FT_Face, len(ft_coords), ft_coords)
    
    def setGlyph(self, glyph_id):
        self.glyph_id = glyph_id
        flags = freetype.FT_LOAD_DEFAULT #| freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_NO_BITMAP
        flags = freetype.FT_LOAD_DEFAULT | freetype.FT_LOAD_NO_SCALE
        if isinstance(glyph_id, int):
            self.font.load_glyph(glyph_id, flags)
        else:
            self.font.load_char(glyph_id, flags)

    def drawOutlineToPen(self, glyph_id, pen):
        self.setGlyph(glyph_id)
        outline = self.font.glyph.outline
        rp = DATPen()
        self.font.glyph.outline.decompose(rp, move_to=FreetypeReader.moveTo, line_to=FreetypeReader.lineTo, conic_to=FreetypeReader.conicTo, cubic_to=FreetypeReader.cubicTo)
        if len(rp.value) > 0:
            rp.closePath()
        rp.replay(pen)
        return
    
    def drawTTOutlineToPen(self, pen):
        glyph_name = self.style.ttfont.getGlyphName(self.glyph_id)
        g = self.style.ttfont.getGlyphSet()[glyph_name]
        try:
            g.draw(pen)
        except TypeError:
            print("could not draw TT outline")
            
    def moveTo(a, pen):
        if len(pen.value) > 0:
            pen.closePath()
        pen.moveTo((a.x, a.y))

    def lineTo(a, pen):
        pen.lineTo((a.x, a.y))

    def conicTo(a, b, pen):
        if False:
            pen.qCurveTo((a.x, a.y), (b.x, b.y))
        else:
            start = pen.value[-1][-1][-1]
            pen.curveTo(*raise_quadratic(start, (a.x, a.y), (b.x, b.y)))
            #pen.lineTo((b.x, b.y))

    def cubicTo(a, b, c, pen):
        pen.curveTo((a.x, a.y), (b.x, b.y), (c.x, c.y))


class FittableMixin():
    def textContent(self):
        print("textContent() not overwritten")

    def fit(self, width):
        current_width = self.width()
        tries = 0
        if current_width > width: # need to shrink
            while tries < 1000 and current_width > width:
                adjusted = self.shrink()
                #for s in self.slugs:
                #    adjusted = s.shrink() or adjusted
                if adjusted:
                    tries += 1
                    current_width = self.width()
                else:
                    #print(">>> TOO BIG :::", self.textContent())
                    return self
        elif current_width < width: # need to expand
            pass
        return self


class GrafStyle():
    def __init__(self, leading=10, x="centerx", xp=0, **kwargs):
        self.leading = kwargs.get("l", leading)
        self.x = x
        self.xp = xp


class Graf():
    def __init__(self, lines, container, style=None, **kwargs):
        if isinstance(container, Rect):
            self.container = DATPen().rect(container)
        else:
            self.container = container
        if style and isinstance(style, GrafStyle):
            self.style = style
        else:
            self.style = GrafStyle(**kwargs)
        self.lines = lines
    
    def lineRects(self):
        # which came first, the height or the width???
        rects = []
        leadings = []
        box = self.container.getFrame()
        leftover = box
        for l in self.lines:
            box, leftover = leftover.divide(l.height(), "maxy")
            leading, leftover = leftover.divide(self.style.leading, "maxy")
            leadings.append(leading)
            rects.append(box)
        return rects
    
    def width(self):
        return max([l.width() for l in self.lines])

    def fit(self):
        rects = self.lineRects()
        for idx, l in enumerate(self.lines):
            l.fit(rects[idx].w - self.style.xp)
        return self
    
    def pens(self):
        rects = self.lineRects()
        pens = DATPenSet()
        for idx, l in enumerate(self.lines):
            r = rects[idx]
            dps = l.pens().translate(r.x, r.y)
            dps.container = r
            dps.align(dps.container, x=self.style.x, y=None)
            pens.pens.append(dps)
        return pens
    
    def fpa(self, rect=None):
        return self.fit().pens().align(rect or self.container.getFrame())


class Lockup(FittableMixin):
    def __init__(self, slugs):
        self.slugs = slugs
    
    def width(self):
        return sum([s.width() for s in self.slugs])
    
    def height(self):
        return max([s.height() for s in self.slugs])
    
    def textContent(self):
        return "/".join([s.textContent() for s in self.slugs])

    def shrink(self):
        adjusted = False
        for s in self.slugs:
            adjusted = s.shrink() or adjusted
        return adjusted

    def pens(self):
        pens = []
        x_off = 0
        for s in self.slugs:
            x_off += s.margin[0]
            dps = s.pens()
            dps.translate(x_off, 0)
            pens.extend(dps.pens)
            x_off += dps.getFrame().w
            x_off += s.margin[1]
            x_off += s.strings[-1].tracking
        return DATPenSet(pens)
    
    def pen(self):
        return self.pens().pen()
    
    def TextToLines(text, primary, fallback=None):
        lines = []
        for line in text.split("\n"):
            lines.append(Lockup([Slug(line, primary, fallback)]))
        return lines
    
    def SlugsToLines(slugs):
        return [Lockup([slug]) for slug in slugs]


def T2L(text, primary, fallback=None):
    return Lockup.TextToLines(text, primary, fallback)


class Slug(FittableMixin):
    def __init__(self, text, primary, fallback=None, margin=[0, 0]):
        self.text = text
        self.primary = primary
        self.fallback = fallback
        self.margin = margin
        self.strings = []
        self.tag()
    
    def tag(self):
        if self.fallback:
            segments = segment(self.text, "LATIN")
            self.strings = [StyledString(s[1], self.fallback if "LATIN" in s[0] else self.primary) for s in segments]
        else:
            self.strings = [StyledString(self.text, self.primary)]
    
    def width(self):
        return sum([s.width() for s in self.strings])
    
    def height(self):
        return max([s.style.capHeight*s.scale() for s in self.strings])
    
    def textContent(self):
        return "-".join([s.textContent() for s in self.strings])

    def shrink(self):
        adjusted = False
        for s in self.strings:
            adjusted = s.shrink() or adjusted
        return adjusted

    def pens(self, atomized=True):
        pens = DATPenSet()
        x_off = 0
        for s in self.strings:
            #x_off += s.margin[0]
            if atomized:
                dps = s.pens(frame=True)
                if dps.layered:
                    pens.layered = True
                dps.translate(x_off, 0)
                pens.pens.extend(dps.pens)
                x_off += dps.getFrame().w
            else:
                dp = s.pen(frame=True)
                dp.translate(x_off, 0)
                pens.pens.append(dp)
                x_off += dp.getFrame().w
            #x_off += dps.getFrame().w
            #x_off += s.margin[1]
        return pens
        #return DATPenSet([s.pens(frame=True) for s in self.strings])
    
    def pen(self):
        return self.pens(atomized=False).pen()


_prefixes = [
    ["¬", "~/Library/Fonts"],
    ["≈", "~/Type/fonts/fonts"],
]


class Style():
    def RegisterShorthandPrefix(prefix, expansion):
        global _prefixes
        _prefixes.append([prefix, expansion])

    def __init__(self,
            font=None,
            fontSize=12,
            ttFont=None,
            tracking=0,
            trackingLimit=0,
            kern=dict(), # custom kerning
            space=None,
            baselineShift=0,
            xShift=None,
            variations=dict(),
            variationLimits=dict(),
            increments=dict(),
            features=dict(),
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
            preventHwid=False,
            layer=None,
            **kwargs):
        """
        kern (k) — a dict of glyphName->[left,right] values in font-space
        tracking (t)
        trackingLimit (tl)
        baselineShift (bs)
        capHeight (ch) — A number in font-space; not specified, read from font; specified as 'x', capHeight is set to xHeight as read from font
        """

        self.next = None

        try:
            # Load a font directly from a font-authoring in-memory object
            if isinstance(font, Font): # defcon
                self.fontFile = "<in-memory>.ufo"
                self.ufo = True
                self.format = "ufo"
                ufo = font
            else:
                raise Exception("Not in-memory")
        except:
            # Load a font from a file
            if isinstance(font, str):
                self.fontFile = self.normalizeFontPath(font)
            else:
                self.fontFile = self.normalizeFontPath(font[0])
                if len(font) > 1:
                    self.next = Style(font=font[1:], fontSize=fontSize, ttFont=ttFont, tracking=tracking, trackingLimit=trackingLimit, kern=kern, space=space, baselineShift=baselineShift,xShift=xShift, variations=variations, variationLimits=variationLimits, increments=increments, features=features, varyFontSize=varyFontSize, fill=fill,stroke=stroke, strokeWidth=strokeWidth, palette=palette, capHeight=capHeight, data=data, latin=latin, lang=lang, filter=filter, preventHwid=preventHwid, layer=layer, **kwargs)
            
            self.format = os.path.splitext(self.fontFile)[1][1:]
            self.ufo = self.format == "ufo"
            self.layer = layer

            if self.ufo:
                ufo = Font(self.fontFile)
            if self.format == "glyphs":
                ufo = glyphsLib.load_to_ufos(self.fontFile)[0]
                self.ufo = True

        capHeight = kwargs.get("ch", capHeight)

        if self.ufo:
            self.ttfont = None
            self.fontdata = None
            self.font = ufo
            self.glyphSet = self.font
            if self.layer:
                self.glyphSet = self.font.layers[self.layer]
            self.upem = self.font.info.unitsPerEm
            self.capHeight = self.font.info.capHeight
        else:
            try:
                self.ttfont = ttFont or TTFont(self.fontFile) # could cache this?
            except:
                self.ttfont = None
            self.fontdata = get_cached_font(self.fontFile)
            self.upem = hb.Face(self.fontdata).upem
            try:
                os2 = self.ttfont["OS/2"]
                self.capHeight = os2.sCapHeight
                self.xHeight = os2.sxHeight
                if capHeight == "x":
                    self.capHeight = self.xHeight
            except:
                self.capHeight = 1000 # alternative?
        
        if capHeight: # override whatever the font says
            if capHeight != "x":
                self.capHeight = capHeight

        self.fontSize = fontSize
        self.tracking = kwargs.get("t", tracking)
        self.kern = kwargs.get("k", kern)
        self.trackingLimit = kwargs.get("tl", trackingLimit)
        self.baselineShift = kwargs.get("bs", baselineShift)
        self.xShift = kwargs.get("xs", xShift)
        self.palette = palette
        self.lang = lang
        self.filter = filter
        self.data = data
        self.latin = latin
        self.preventHwid = preventHwid

        # TODO should be able to pass in as kwarg
        found_features = features.copy()
        for k, v in kwargs.items():
            if k.startswith("ss") and len(k) == 4:
                found_features[k] = v
            if k in ["dlig", "swsh", "onum", "tnum", "palt"]:
                found_features[k] = v
        self.features = {**dict(kern=True, liga=True), **found_features}

        self.increments = increments
        self.space = space

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
        
        if not self.ufo:
            try:
                fvar = self.ttfont['fvar']
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
        
    def normalizeFontPath(self, font):
        global _prefixes
        ff = font
        for prefix, expansion in _prefixes:
            ff = ff.replace(prefix, expansion)
        return os.path.expanduser(ff) 

    def mod(self, **kwargs):
        ns = copy.deepcopy(self)
        for k, v in kwargs.items():
            setattr(ns, k, v)
        return ns
    
    def addVariations(self, variations, limits=dict()):
        for k, v in self.normalizeVariations(variations).items():
            self.variations[k] = v
        for k, v in self.normalizeVariations(limits).items():
            self.variationLimits[k] = v
    
    def normalizeVariations(self, variations):
        if variations.get("scale") != None:
            scale = variations["scale"]
            del variations["scale"]
        else:
            scale = True
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
                variations[k] = float((axis.maxValue-axis.minValue)*v + axis.minValue)
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
    
    def listFeatures(self):
        font = self.ttfont
        all_features = OrderedDict()
        tag = "GSUB"
        if not tag in font: return
        table = font[tag].table
        if not table.ScriptList or not table.FeatureList: return
        featureRecords = table.FeatureList.FeatureRecord
        for script in table.ScriptList.ScriptRecord:
            _script = {}
            if not script.Script: continue
            # script.scriptTag
            languages = list(script.Script.LangSysRecord)
            if script.Script.DefaultLangSys:
                defaultlangsys = otTables.LangSysRecord()
                defaultlangsys.LangSysTag = "default"
                defaultlangsys.LangSys = script.Script.DefaultLangSys
                languages.insert(0, defaultlangsys)
            for langsys in languages:
                # langsys.LangSysTag
                if not langsys.LangSys:
                    continue
                features = [featureRecords[index] for index in langsys.LangSys.FeatureIndex]
                for feature in features:
                    # feature.FeatureTag
                    if feature.FeatureTag not in all_features:
                        try:
                            name = font["name"].getName(feature.Feature.FeatureParams.UINameID, 3, 1).toUnicode()
                        except:
                            name = True
                        all_features[feature.FeatureTag] = name
        return all_features
    
    def stylisticSets(self):
        all_features = self.listFeatures()
        return [(k, v) for (k, v) in all_features.items() if k.startswith("ss")]


class StyledString(FittableMixin):
    def __init__(self, text, style):
        self.text = text
        self.setStyle(style)
        
        if self.style.ufo:
            pass
        else:
            self.glyphs = self.hb.glyphs(self.variations, self.features)
    
    def setStyle(self, style):
        self.style = style
        # these will change based on fitting, so we make copies
        self.fontSize = self.style.fontSize
        self.tracking = self.style.tracking
        self.features = self.style.features.copy()
        self.variations = self.style.variations.copy()

        self.hb = Harfbuzz(self.style.fontdata,
            text=self.text,
            height=self.style.capHeight,
            lang=self.style.lang,
            ttfont=self.style.ttfont,
            kern=self.style.kern)
    
    def trackFrames(self, frames):
        t = self.tracking
        x_off = 0
        for idx, f in enumerate(frames):
            f.frame = f.frame.offset(x_off, 0)
            x_off += t
            if self.style.space and f.glyphName.lower() == "space":
                x_off += self.style.space
        return frames
    
    def adjustFramesForPath(self, frames):
        for idx, f in enumerate(frames):    
            if self.style.xShift:
                try:
                    f.frame.x += self.style.xShift[idx]
                except:
                    pass
        return frames
    
    # def getGlyphNames(self, txt):
    #     frames = Harfbuzz.GetFrames(self.style.fontdata, text=txt, axes=self.variations, features=self.features, height=self.style.capHeight)
    #     glyph_names = []
    #     for f in frames:
    #         glyph_names.append(self.style.ttfont.getGlyphName(f.gid))
    #     return glyph_names

    def TextToGuessedGlyphNames(text):
        glyph_names = []
        current = None
        for t in text:
            glyph = None
            if t == "{":
                current = ""
            elif t == "}":
                glyph = current
                current = None
            elif current is not None:
                current += t
            elif t == ",":
                glyph = "comma"
            elif t == " ":
                glyph = "space"
            elif t == ".":
                glyph = "period"
            elif t == "1":
                glyph = "one"
            elif t == "2":
                glyph = "two"
            elif t == "3":
                glyph = "three"
            elif t == "4":
                glyph = "four"
            elif t == "5":
                glyph = "five"
            elif t == "6":
                glyph = "six"
            elif t == "7":
                glyph = "seven"
            elif t == "8":
                glyph = "eight"
            elif t == "9":
                glyph = "nine"
            elif t == "’":
                glyph = "quoteright"
            elif re.match(r"[A-Za-z]", t):
                glyph = t
            else: # convert unicode literals to uni*-style
                glyph = hex(ord(t)).upper().replace("0X", "uni")
            if glyph:
                glyph_names.append(glyph)
        return glyph_names
    
    def getGlyphFrames(self):
        frames = []
        glyph_names = []

        if self.style.ufo:
            glyph_names = StyledString.TextToGuessedGlyphNames(self.text)
            x_off = 0
            for g in glyph_names:
                try:
                    glif = self.style.glyphSet[g]
                    if glif.bounds == None and "space" not in g:
                        g = ".notdef"
                        glif = self.style.glyphSet[".notdef"]
                except:
                    g = ".notdef"
                    glif = self.style.glyphSet[".notdef"]
                w = glif.width
                r = Rect(x_off, 0, w, self.style.capHeight)
                x_off += w
                frames.append(HarfbuzzFrame(g, dict(), Point((0, 0)), r, g))
        else:
            frames = self.hb.frames(self.variations, self.features, self.glyphs)
        
        for f in frames:
            f.frame = f.frame.scale(self.scale())

        return self.adjustFramesForPath(self.trackFrames(frames))
    
    def width(self): # size?
        return self.getGlyphFrames()[-1].frame.point("SE").x
    
    def scale(self):
        return self.fontSize / self.style.upem
    
    def textContent(self):
        return self.text

    def shrink(self):
        adjusted = False
        if self.tracking > 0:
            self.tracking -= self.style.increments.get("tracking", 0.25)
            adjusted = True
        else:
            for k, v in self.style.variationLimits.items():
                if self.variations[k] > self.style.variationLimits[k]:
                    self.variations[k] -= self.style.increments.get(k, 1)
                    adjusted = True
                    break
        if not adjusted and self.tracking > self.style.trackingLimit:
            self.tracking -= self.style.increments.get("tracking", 0.25)
            adjusted = True
        if not adjusted and self.style.varyFontSize:
            self.fontSize -= 1
            adjusted = True
        if not adjusted and self.style.next:
            self.setStyle(self.style.next)
            adjusted = True
        if not adjusted and self.style.preventHwid == False and "hwid" not in self.features and not self.style.ufo:
            self.features["hwid"] = True
            self.tracking = self.style.tracking # reset to widest
            self.glyphs = self.hb.glyphs(self.variations, self.features)
            adjusted = True
        return adjusted
    
    def formattedString(self):
        if _drawBot:
            feas = dict(self.features)
            del feas["kern"]
            return _drawBot.FormattedString(self.text, font=self.fontFile, fontSize=self.fontSize, lineHeight=self.fontSize+2, tracking=self.tracking, fontVariations=self.variations, openTypeFeatures=feas)
        else:
            print("No DrawBot available")
            return None
    
    def drawFrameToPen(self, fr, idx, pen, frame, gid, useTTFont=False):
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
        t = t.translate(frame.frame.x/self.scale(), frame.frame.y/self.scale())
        #t = t.translate(0, bs)
        tp = TransformPen(pen, (t[0], t[1], t[2], t[3], t[4], t[5]))
        
        dp = DATPen()
        if useTTFont:
            fr.drawTTOutlineToPen(gid, dp)
        else:
            fr.drawOutlineToPen(gid, dp)
        
        # apply full-scale filtering before transform-down
        if self.style.filter:
            dp = self.style.filter(frame.frame, dp)
        
        dp.replay(tp)
    
    def drawToPen(self, pen, frames, index=None, useTTFont=False):
        if self.style.ufo:
            shape_reader = UFOShapeReader(self.style)
        else:
            shape_reader = FreetypeReader(self.style)
        
        shape_reader.setVariations(self.variations)

        if self.style.ttfont and "COLR" in self.style.ttfont:
            colr = self.style.ttfont["COLR"]
            cpal = self.style.ttfont["CPAL"]
        else:
            colr = None
            cpal = None

        for idx, frame in enumerate(frames):
            if index is not None and idx != index:
                continue
            if colr and cpal:
                gn = self.style.ttfont.getGlyphName(frame.gid)
                layers = colr[gn]
                dps = DATPenSet()
                dps.layered = True
                if layers:
                    for layer in layers:
                        gid = self.style.ttfont.getGlyphID(layer.name)
                        dp = DATPen()
                        self.drawFrameToPen(shape_reader, idx, dp, frame, gid, useTTFont=useTTFont)
                        dp.attr(fill=cpal.palettes[self.style.palette][layer.colorID])
                        if len(dp.value) > 0:
                            dps.addPen(dp)
                else:
                    print("No layers found for ", gn)
                dps.replay(pen)
                return dps # TODO weird to return in a for-loop isn't it?
            else:
                self.drawFrameToPen(shape_reader, idx, pen, frame, frame.gid, useTTFont=useTTFont)
    
    def _emptyPenWithAttrs(self):
        attrs = dict(fill=self.style.fill)
        if self.style.stroke:
            attrs["stroke"] = dict(color=self.style.stroke, weight=self.style.strokeWidth)
        dp = DATPen(**attrs)
        return dp

    def pens(self, frame=True):
        self._frames = self.getGlyphFrames()
        pens = DATPenSet()
        for idx, f in enumerate(self._frames):
            dp_atom = self._emptyPenWithAttrs()
            dps = self.drawToPen(dp_atom, self._frames, index=idx)
            if dps:
                if dps.layered:
                    pens.layered = True
                dp_atom = dps
            if frame:
                f.frame.y = 0
                #if f.frame.y < 0:
                #    f.frame.y = 0
                dp_atom.addFrame(f.frame)
            pens.addPen(dp_atom)
        return pens

    def pen(self, frame=True):
        dp = self._emptyPenWithAttrs()
        self._frames = self.getGlyphFrames()
        self.drawToPen(dp, self._frames)
        if frame:
            dp.addFrame(Rect((0, 0, self.width(), self.style.capHeight*self.scale())))
            dp.typographic = True
        return dp


if __name__ == "__main__":
    from coldtype.color import Gradient
    from coldtype.viewer import previewer
    from random import randint
    from coldtype.pens.svgpen import SVGPen
    
    def ss_bounds_test(font, preview):
        #f = f"≈/{font}.ttf"
        f = font
        r = Rect((0, 0, 700, 120))
        ss = StyledString("ABC", font=f, fontSize=100, variations=dict(wght=1, wdth=1,  scale=True), features=dict(ss01=True))
        dp = ss.pen()
        dp.translate(20, 20)
        #r = svg.rect.inset(50, 0).take(180, "centery")
        #dp.align(r)
        dpf = DATPen(fill=None, stroke=dict(color=("random", 0.5), weight=4))
        for f in ss._frames:
            dpf.rect(f.frame)
        dpf.translate(20, 20)
        if "HVAR" in ss.ttfont:
            #print(ss.ttfont["HVAR"], font)
            pass
        else:
            print(">>>>>>>>>>>>>>>>>>>> NO HVAR", font)
        preview.send(SVGPen.Composite([dp, dpf], r), r)
    
    def ss_and_shape_test(preview):
        r = Rect((0, 0, 500, 120))
        f, v = ["≈/Nonplus-Black.otf", dict()]
        ss1 = Slug("Yoy! ", Style(font=f, variations=v, fontSize=80, baselineShift=5))
        f, v = ["¬/Fit-Variable.ttf", dict(wdth=0.1, scale=True)]
        ps2 = Slug("ABC", Style(font=f, variations=v, fontSize=72)).pens().rotate(-10)
        oval = DATPen().polygon(3, Rect(0, 0, 50, 50)).attr(fill="random")
        ss1_p = ss1.pen().attr(fill="darkorchid")
        #print(ss1_p.frame)
        dps = DATPenSet(
            ss1_p,
            ps2,
            oval
            )
        dps.distribute()
        dps.align(r)
        preview.send(SVGPen.Composite(dps.pens + [DATPen.Grid(r, y=4)], r), r)

    def rotalic_test(preview):
        r = Rect(0, 0, 500, 200)
        ps = Slug("Side", Style("≈/Vinila-VF-HVAR-table.ttf", 200, variations=dict(wdth=0.5, wght=0.7, scale=True))).pens().rotate(-15).align(r)
        preview.send(SVGPen.Composite(
            [DATPen.Grid(r)] + 
            ps.pens + 
            ps.frameSet().pens, r), r)

    def multilang_test(p):
        obv = Style("≈/ObviouslyVariable.ttf", 80, wdth=1, wght=0.7, fill=(1, 0, 0.5))
        r = Rect((0, 0, 600, 140))
        _s = [
            "(رطب (ما قبل",
            "(جاف + رطب (ما قبل",
            "+بوابة",
            "A الملخبط",
            "Ali الملخبط Boba",
            "الكروسفِيد",
            "مستوَى التخفيف",
            "اللٌُوفَاي",
            "9رقمي: سنوات ال0",
        ]
        style = Style("≈/GretaArabicCondensedAR-Heavy.otf",
                100,
                lang="ar",
                fill=Gradient.Random(r))
        lck = Slug(_s[-1], style, obv).fit(r.w - 100)
        dps = lck.pens()
        dps.align(r)
        g = DATPen.Grid(r, y=4)
        p.send(SVGPen.Composite([
            g,
            dps.frameSet().attr(fill=None, stroke=0),
            dps
            ], r), r)

    def cjk_multilang_test(p):
        obv = Style("≈/ObviouslyVariable.ttf", 80, wdth=1, wght=0.7, fill=(1, 0, 0.5))
        r = Rect((0, 0, 600, 140))
        _s = [
            "BPM同步"
        ]
        style = Style("≈/HiraginoSansGBW3.ttf",
                100,
                #lang="zh",
                fill=Gradient.Random(r))
        lck = Slug(_s[0], style, obv).fit(r.w - 100)
        dps = lck.pens()
        dps.align(r)
        g = DATPen.Grid(r, y=4)
        p.send(SVGPen.Composite([
            g,
            dps.frameSet().attr(fill=None, stroke=0),
            dps
            ], r), r)
    
    def tracking_test(p):
        r = Rect(0, 0, 500, 100)
        s1 = Slug("ABC", Style("≈/VulfSans-Medium.otf", 100, tracking=0, fill=("random", 0.2), strokeWidth=2, stroke=("random", 0.75)))
        s2 = Slug("xyz", Style("≈/VulfSans-Black.otf", 100, baselineShift=0, fill=("random", 0.1), strokeWidth=2, stroke=("random", 0.75)))
        ps1 = s1.pens()
        ps1.align(r)
        ps2 = s2.pens()
        ps2.align(r)
        frames = []
        p.send(SVGPen.Composite(
            frames + ps1.pens + ps2.pens + [DATPen.Grid(r, x=6, y=4)], r), r)

    def color_font_test(p):
        r = Rect(0,0,600,300)
        f = "≈/PappardelleParty-VF.ttf"
        t = "XYZ/yoyoma"
        st = Style(f, 300, palette=0, ss09=1)
        pprint(st.stylisticSets())
        ps = Slug(t, st).pens().align(r, tv=0).flatten()
        p.send(SVGPen.Composite([
            #ps.frameSet(),
            ps,
            ], r), r)

    def hoi_test(p):
        r = Rect(0,0,300,300)
        f = "≈/SpaceMonoHOI_2_cubic.ttf"
        st = Style(f, 100, wght=1, slnt=1, ital=0.65, ITA2=0.65, ITA3=0.65, MONO=1)
        ps = Slug("Ran", st).pen().align(r).attr(fill="random")
        p.send(SVGPen.Composite([ps], r), r)

    def emoji_test(p):
        r = Rect(0,0,500,200)
        f = "≈/TwemojiMozilla.ttf"
        t = "🍕💽 🖥"
        ps = Slug(t, Style(f, 100, t=20, ch=500, bs=11)).pens().align(r, tv=0).flatten()
        print("Layered", ps.layered)
        p.send(SVGPen.Composite([
            ps,
            ps.frameSet(),
            ], r), r)
    
    def ufo_test(p):
        r = Rect(0, 0, 500, 200)
        f = "~/Type/grafprojects/scratch2/megalodon.ufo"
        style = Style(f, 300, layer="person", fill=None, stroke=0, strokeWidth=1)
        slug = Slug("{megalodon}", style).fit(r.w)
        p.send(SVGPen.Composite(slug.pen().align(r, th=0), r), r)
    
    def glyphs_test(p):
        r = Rect(0, 0, 500, 200)
        f = "~/Downloads/vulf_compressor/vulf_compressor.glyphs"
        style = Style(f, 200, t=-10, varyFontSize=True)
        slug = Slug("ABC一低保真度", style).fit(r.w)
        p.send(SVGPen.Composite(slug.pen().align(r).removeOverlap().attr(fill="random"), r), r)
    
    def multiline_test(p):
        r = Rect(0, 0, 300, 300)
        f = "≈/ObviouslyVariable.ttf"
        style = Style(f, 50, wdth=1, wght=1, slnt=1, fill=0)
        graf = Graf(Lockup.TextToLines("Hello\n—\nYoyoyo\nMa", style), DATPen().rect(r.take(100, "centerx")))
        graf.fit()
        p.send(SVGPen.Composite(graf.pens().align(r), r), r)
    
    def multiline_fit_test(p):
        r = Rect(0, 0, 300, 300)
        f = "≈/Vinila-VF-HVAR-table.ttf"
        style = Style(f, 50, wdth=1, wght=1, fill=0, ss01=True)
        pprint(style.stylisticSets())
        graf = Graf(Lockup.TextToLines("T\nI\nE\nM\nP\nO", style), DATPen().rect(r.take(30, "centerx")))
        graf.fit()
        p.send(SVGPen.Composite(graf.pens().align(r), r), r)
    
    def language_hb_test(p):
        r = Rect(0, 0, 300, 100)
        f = "¬/SourceSerifPro-Black.ttf"
        style = Style(f, 50, wdth=1, wght=1, ss01=True)
        dp1 = Slug("ríjks б", style.mod(lang="nl")).pen().align(r)
        p.send(SVGPen.Composite(dp1, r), r)
    
    def custom_kern_test(p):
        f = "≈/VulfMonoLightItalicVariable.ttf"
        r = Rect(0, 0, 300, 100)
        style = Style(f, 50, wdth=0.2, kern=dict(eacute=[0, -300]))
        dp1 = Slug("stéréo", style).pen().attr(fill="random").align(r)
        p.send(SVGPen.Composite(dp1, r), r)
    
    def hwid_test(p):
        f = "≈/HeiseiMaruGothicStdW8.otf"
        r = Rect(0, 0, 300, 100)
        style = Style(f, 30, wdth=0.2, kern=dict(eacute=[0, -300]), bs=lambda i: randint(-20, 20))
        dp1 = Slug("イージーオペレーションディザー", style).fit(r.w).pen().align(r)
        p.send(SVGPen.Composite(dp1, r), r)
    
    def interp_test(p):
        f = "≈/ObviouslyVariable.ttf"
        r = Rect(0, 0, 700, 300)
        dps = DATPenSet()
        l = 30
        for x in range(l):
            style = Style(f, 272, wdth=x/l, wght=0, slnt=1, fill=(0, 0.2))
            dp = Slug("HELLO", style).pen().align(r).removeOverlap()
            dps.addPen(dp)
        p.send(SVGPen.Composite(dps, r), r)
    
    def family_test(p):
        f = ["≈/Konsole0.2-Wide.otf", "≈/Konsole0.2-Regular.otf", "≈/Konsole0.2-Compact.otf"]
        r = Rect(0, 0, 300, 100)
        style = Style(f, 60, fill=(1, 0, 0.5))
        dp1 = Slug("Hello world", style).fit(r.w).pen().align(r)
        p.send(SVGPen.Composite(dp1, r), r)
    
    def layered_font_test(p):
        r = Rect(0, 0, 1000, 100)
        
        def layered_slugs(txt):
            return [
                Slug(txt, Style("≈/CaslonAntique-Shaded-Fill.otf", 60, fill=(1, 0, 0), t=-20)),
                Slug(txt, Style("≈/CaslonAntique-Shaded-Shadow.otf", 60, fill=(0, 0, 1), t=-20))
            ]
        
        s1, s2 = layered_slugs("Hello wor")
        s3, s4 = layered_slugs("ld")
        #dp1 = s1.pen().align(r, th=0)
        #dp2 = s2.pen().align(r, th=0)

        lck = Lockup([s1, s3])
        lck2 = Lockup([s2, s4])
        
        p.send(SVGPen.Composite([
            lck2.pens().align(r, th=0),
            lck.pens().align(r, th=0)
            ], r), r)
    
    def cache_width_test(p):
        #from itertools import chain
        #from fontTools.unicode import Unicode
        f = "~/Goodhertz/plugin-builder/configs/builder/design/GhzNumbersCompressed.ufo"
        r = Rect(0, 0, 300, 100)
        style = Style(f, 30)
        #glyphs = []
        #lookup = {}
        #for g in sorted(style.font, key=lambda g: g.name):
        #    lookup[g.name] = g.width
        #print(lookup)
        #print(style.font)
        #ttf = style.ttfont
        #print(style.ttfont["cmap"].tables)
        #chars = chain.from_iterable([y + (Unicode[y[0]],) for y in x.cmap.items()] for x in ttf["cmap"].tables)
        #for _, c, _ in sorted(set(chars)):
        #    print(c)
        gn = StyledString.TextToGuessedGlyphNames("1.23{uniE801}")
        print(gn)
        dp1 = Slug("1.23{uniE801}", style).fit(r.w).pen().align(r)
        p.send(SVGPen.Composite(dp1, r), r)

    with previewer() as p:
        if False:
            ss_bounds_test("≈/ObviouslyVariable.ttf", p)
            #ss_bounds_test("≈/MutatorSans.ttf", p)
            ss_bounds_test("≈/VinilaVariable.ttf", p)
            ss_bounds_test("≈/Vinila-VF-HVAR-table.ttf", p)
            #ss_bounds_test("≈/Compressa-MICRO-GX-Rg.ttf", p)
            #ss_bounds_test("≈/BruphyGX.ttf", p)
        
        #ss_and_shape_test(p)
        #rotalic_test(p)
        #multilang_test(p)
        #cjk_multilang_test(p)
        #tracking_test(p)
        #color_font_test(p)
        #emoji_test(p)
        #hoi_test(p)
        ufo_test(p)
        #glyphs_test(p)
        #multiline_test(p)
        #hwid_test(p)
        #multiline_fit_test(p)
        #language_hb_test(p)
        #custom_kern_test(p)
        #interp_test(p)
        #cache_width_test(p)
        #family_test(p)
        #layered_font_test(p)
