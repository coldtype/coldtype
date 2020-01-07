import math
import copy
import re
import os

from pathlib import Path
from collections import OrderedDict

import freetype
from freetype.raw import *

import unicodedata
import uharfbuzz as hb

from fontTools.ttLib.tables import otTables
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.pens.boundsPen import ControlBoundsPen, BoundsPen
from fontTools.ufoLib import UFOReader
from fontTools.ttLib import TTFont

from coldtype.beziers import raise_quadratic
from coldtype.color import normalize_color
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.geometry import Rect, Point

import Levenshtein

from defcon import Font
import glyphsLib

try:
    import drawBot as _drawBot
    import CoreText
    import AppKit
    import Quartz
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
        return f"HarfbuzzFrame:({self.glyphName}>>>{self.frame}(gid{self.gid})"


class Harfbuzz():
    def __init__(self,
                 fontdata,
                 text="",
                 height=1000,
                 lang=None,
                 ttfont=None):
        self.face = hb.Face(fontdata)
        self.ttfont = ttfont
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
        last_gn = None
        for idx, (info, pos) in enumerate(zip(infos, positions)):
            kern_shift = 0
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
            frames.append(HarfbuzzFrame(gid, info, pos, Rect(x+x_offset, y_offset, x_advance, self.height), gn)) # 100?
            x += x_advance + kern_shift
            last_gn = gn
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
        if isinstance(width, Rect):
            width = width.w
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


_prefixes = [
    ["¬", "~/Library/Fonts"],
    ["≈", "~/Type/fonts/fonts"],
    ["ç", str(Path(__file__).parent.parent.parent.joinpath("assets").resolve())]
]

def normalize_font_path(font):
    global _prefixes
    ff = font
    for prefix, expansion in _prefixes:
        ff = ff.replace(prefix, expansion)
    literal = Path(ff).expanduser()
    ufo = literal.suffix == ".ufo"
    if literal.exists() and (not literal.is_dir() or ufo):
        return str(literal)
    else:
        fonts = list(literal.parent.glob("**/*.ttf"))
        fonts.extend(list(literal.parent.glob("**/*.otf")))
        matches = []
        match_terms = literal.name.split(" ")
        for font in fonts:
            if font.is_dir():
                continue
            if all([mt in font.name for mt in match_terms]):
                matches.append(font)
        if matches:
            matches.sort()
            matches.reverse()
            distances = [Levenshtein.distance(m.name, literal.name) for m in matches]
            match = matches[distances.index(min(distances))]
            print(">>>>> FONTMATCH:", literal.name, "<to>", match.name)
            return str(match)
        else:
            raise Exception("NO FONT FOUND FOR", literal)


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
            trackingMode=0,
            kern=dict(), # custom kerning TODO actually more of a side-bearing adjustment
            kern_pairs=dict(),
            overlap_pairs=dict(),
            overlap_outline=3,
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
            layerer=None,
            preventHwid=False,
            layer=None,
            printAxes=False,
            printFeatures=False,
            db=False,
            reverse=False,
            removeOverlap=False,
            rotate=0,
            **kwargs):
        """
        kern (k) — a dict of glyphName->[left,right] values in font-space
        tracking (t)
        trackingLimit (tl)
        baselineShift (bs)
        capHeight (ch) — A number in font-space; not specified, read from font; specified as 'x', capHeight is set to xHeight as read from font
        """

        self.db = db
        self.next = None
        self.layer = layer
        self.layerer = layerer
        self.reverse = kwargs.get("r", reverse)
        self.removeOverlap = kwargs.get("ro", removeOverlap)
        self.rotate = rotate

        self.format = None
        # Load a font from a file
        if isinstance(font, Font):
            self.fontFile = "<in-memory>.ufo"
            self.ufo = True
            self.format = "ufo"
            ufo = font
        elif isinstance(font, str):
            self.fontFile = normalize_font_path(font)
        elif isinstance(font, Path):
            self.fontFile = normalize_font_path(str(font))
        else:
            self.fontFile = normalize_font_path(font[0])
            if len(font) > 1:
                self.next = Style(font=font[1:], fontSize=fontSize, ttFont=ttFont, tracking=tracking, trackingLimit=trackingLimit, kern=kern, space=space, baselineShift=baselineShift,xShift=xShift, variations=variations, variationLimits=variationLimits, increments=increments, features=features, varyFontSize=varyFontSize, fill=fill,stroke=stroke, strokeWidth=strokeWidth, palette=palette, capHeight=capHeight, data=data, latin=latin, lang=lang, filter=filter, preventHwid=preventHwid, layer=layer, **kwargs)
        
        if not self.format:
            self.format = os.path.splitext(self.fontFile)[1][1:]
            self.ufo = self.format == "ufo"

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
        self.kern_pairs = kern_pairs
        self.overlap_pairs = overlap_pairs
        self.overlap_outline = overlap_outline
        self.trackingMode = trackingMode
        self.trackingLimit = kwargs.get("tl", trackingLimit)
        self.baselineShift = kwargs.get("bs", baselineShift)
        self.increments = increments
        self.space = space
        self.xShift = kwargs.get("xs", xShift)
        self.palette = palette
        self.lang = lang
        self.filter = filter
        self.data = data
        self.latin = latin
        self.preventHwid = preventHwid

        if kwargs.get("tu"):
            self.trackingMode = 1
            self.tracking = kwargs.get("tu")
            if not self.increments.get("tracking"):
                self.increments["tracking"] = 5 # TODO good?

        # TODO should be able to pass in as kwarg
        found_features = features.copy()
        if printFeatures:
            print("Coldtype >>>", self.fontFile, "<FEATURES>", found_features)
        for k, v in kwargs.items():
            if k.startswith("ss") and len(k) == 4:
                found_features[k] = v
            if k in ["dlig", "swsh", "onum", "tnum", "palt"]:
                found_features[k] = v
        self.features = {**dict(kern=True, liga=True), **found_features}

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
                    if printAxes:
                        print("Coldtype >>>", self.fontFile, axis.axisTag, axis.minValue, axis.maxValue)
                    self.axes[axis.axisTag] = axis
                    self.variations[axis.axisTag] = axis.defaultValue
                    if axis.axisTag == "wdth": # the only reasonable default
                        self.variationLimits[axis.axisTag] = axis.minValue
                    if axis.axisTag in kwargs and axis.axisTag not in variations:
                        unnormalized_variations[axis.axisTag] = kwargs[axis.axisTag]

            self.addVariations(unnormalized_variations)

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


def offset(x, y, ox, oy):
    return (x + ox, y + oy)

def TransliterateCGPathToBezierPath(data, b):
    bp = data["bp"]
    o = data["offset"]
    op = lambda i: offset(*b.points[i], *o)
    
    if b.type == Quartz.kCGPathElementMoveToPoint:
        bp.moveTo(op(0))
    elif b.type == Quartz.kCGPathElementAddLineToPoint:
        bp.lineTo(op(0))
    elif b.type == Quartz.kCGPathElementAddCurveToPoint:
        bp.curveTo(op(0), op(1), op(2))
    elif b.type == Quartz.kCGPathElementAddQuadCurveToPoint:
        bp.qCurveTo(op(0), op(1))
    elif b.type == Quartz.kCGPathElementCloseSubpath:
        bp.closePath()
    else:
        print(b.type)


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
            ttfont=self.style.ttfont)
    
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
            elif t == "!":
                glyph = "exclam"
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
        elif self.style.db > 0:
            # make a formatted string
            fs = self.formattedString()
            attr_string = fs.getNSObject()
            path = CoreText.CGPathCreateMutable()
            CoreText.CGPathAddRect(path, None, CoreText.CGRectMake(0, 0, 1000000, 1100))
            setter = CoreText.CTFramesetterCreateWithAttributedString(attr_string)
            frame = CoreText.CTFramesetterCreateFrame(setter, (0, 0), path, None)
            ctLines = CoreText.CTFrameGetLines(frame)
            origins = CoreText.CTFrameGetLineOrigins(frame, (0, len(ctLines)), None)
            
            self.ct_glyphs = []
            ct_frames = []
            
            for i, (originX, originY) in enumerate(origins[0:1]): # can only display one 'line' of text
                ctLine = ctLines[i]
                ctRuns = CoreText.CTLineGetGlyphRuns(ctLine)
                for ctRun in ctRuns:
                    attributes = CoreText.CTRunGetAttributes(ctRun) # can be done once out of loop
                    font = attributes.get(AppKit.NSFontAttributeName) # can be done once out of loop
                    baselineShift = attributes.get(AppKit.NSBaselineOffsetAttributeName, 0)
                    glyphCount = CoreText.CTRunGetGlyphCount(ctRun)
                    last_adv = (0, 0)
                    for i in range(glyphCount):
                        glyph = CoreText.CTRunGetGlyphs(ctRun, (i, 1), None)[0]
                        ax, ay = CoreText.CTRunGetPositions(ctRun, (i, 1), None)[0]
                        frame = Rect(ax, ay, 200, 200)
                        ct_frames.append([glyph, frame])
                        glyph_path = CoreText.CTFontCreatePathForGlyph(font, glyph, None)
                        if glyph_path:
                            dp = DATPen()
                            Quartz.CGPathApply(glyph_path, dict(offset=(0, 0), bp=dp), TransliterateCGPathToBezierPath)
                            self.ct_glyphs.append(dp)
                            last_adv = (ax, ay)
            
            for idx, (gid, r) in enumerate(ct_frames):
                glyph = self.glyphs[idx]
                if glyph[0] != gid:
                    raise Exception("Non-matching shaping")
                frames.append(HarfbuzzFrame(gid, dict(), Point((0, 0)), r, glyph[1]))
        else:
            frames = self.hb.frames(self.variations, self.features, self.glyphs)

        if self.style.kern_pairs:
            last_gn = None
            for idx, frame in enumerate(frames):
                gn = frame.glyphName
                for chars, kp in self.style.kern_pairs.items():
                    try:
                        l = kp[0]
                        adv = kp[1]
                    except TypeError:
                        l = kp
                        adv = 0
                    a, b = chars
                    if gn == b and last_gn == a:
                        kern_shift = l
                        if kern_shift != 0:
                            for frame in frames[idx:]:
                                frame.frame.x += kern_shift
                last_gn = gn
        
        if self.style.trackingMode == 1:
            frames = self.trackFrames(frames)

        for f in frames:
            f.frame = f.frame.scale(self.scale())

        if self.style.trackingMode == 0:
            frames = self.trackFrames(frames)

        return self.adjustFramesForPath(frames)
    
    def scale(self):
        return self.fontSize / self.style.upem
    
    def width(self): # size?
        return self.getGlyphFrames()[-1].frame.point("SE").x
    
    def height(self):
        return self.style.capHeight*self.scale()
    
    def textContent(self):
        return self.text

    def shrink(self):
        adjusted = False
        if self.tracking > 0 and self.tracking > self.style.trackingLimit:
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
    
    def formattedString(self, fs=1000):
        if _drawBot:
            feas = dict(self.features)
            del feas["kern"]
            return _drawBot.FormattedString(self.text, font=self.style.fontFile, fontSize=fs, lineHeight=fs+2, fontVariations=self.variations, openTypeFeatures=feas)
        else:
            print("No DrawBot available")
            return None
    
    def scalePenToStyle(self, idx, in_pen, frame):
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
        out_pen = DATPen()
        tp = TransformPen(out_pen, (t[0], t[1], t[2], t[3], t[4], t[5]))
        in_pen.replay(tp)
        if self.style.rotate:
            out_pen.rotate(self.style.rotate)
        return out_pen
    
    def drawFrameToPen(self, reader, idx, frame, gid, useTTFont=False):
        dp = DATPen()
        if self.style.db > 1 and self.ct_glyphs:
            dp.record(self.ct_glyphs[idx])
        elif useTTFont:
            reader.drawTTOutlineToPen(gid, dp)
        else:
            reader.drawOutlineToPen(gid, dp)
        # apply full-scale filtering before transform-down
        if self.style.filter:
            gn = self.style.ttfont.getGlyphName(frame.gid)
            result = self.style.filter(idx, frame.frame, gn, dp)
            if result:
                dp = result
        return dp
    
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
                        #dp = DATPen()
                        dp = self.drawFrameToPen(shape_reader, idx, frame, gid, useTTFont=useTTFont)
                        dp = self.scalePenToStyle(idx, dp, frame)
                        dp.attr(fill=cpal.palettes[self.style.palette][layer.colorID])
                        if len(dp.value) > 0:
                            dps.append(dp)
                else:
                    print("No layers found for ", gn)
                dps.replay(pen)
                return dps # TODO weird to return in a for-loop isn't it?
            else:
                if self.style.layerer:
                    try:
                        gn = self.style.ttfont.getGlyphName(frame.gid)
                    except:
                        gn = frame.gid
                    pen.value = self.drawFrameToPen(shape_reader, idx, frame, frame.gid, useTTFont=useTTFont).value
                    dps = DATPenSet()
                    dps.layered = True
                    dps.append(pen)
                    self.style.layerer(self, gn, pen, dps)
                    for p in dps.pens:
                        p.value = self.scalePenToStyle(idx, p, frame).value
                    return dps
                else:
                    dp = self.drawFrameToPen(shape_reader, idx, frame, frame.gid, useTTFont=useTTFont)
                    dp = self.scalePenToStyle(idx, dp, frame)
                    dp.replay(pen)
    
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
                dp_atom.glyphName = f.glyphName
                if self.style.removeOverlap:
                    dp_atom.removeOverlap()
            pens.append(dp_atom)
                
        if self.style.reverse:
            pens.reversePens()
        
        if self.style.kern_pairs:
            overlap_pairs = {pair:value[2] for (pair, value) in self.style.kern_pairs.items() if not isinstance(value, int) and len(value) > 2}
            pens.overlapPairs(overlap_pairs, outline=self.style.overlap_outline)
        return pens

    def pen(self, frame=True):
        dp = self._emptyPenWithAttrs()
        self._frames = self.getGlyphFrames()
        self.drawToPen(dp, self._frames)
        if frame:
            dp.addFrame(Rect((0, 0, self.width(), self.style.capHeight*self.scale())))
            dp.typographic = True
        return dp