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

from fontgoggles.font import getOpener
from fontgoggles.font.baseFont import BaseFont

try:
    import Levenshtein
except ImportError:
    Levenshtein = None

from defcon import Font
import glyphsLib

try:
    import drawBot as _drawBot
    import CoreText
    import AppKit
    import Quartz
except:
    _drawBot = None



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
    elif Levenshtein:
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
    else:
        raise Exception("FONT LITERAL NOT FOUND")


class FontGoggle():
    # TODO support glyphs?
    def __init__(self, path):
        #ufo = glyphsLib.load_to_ufos(self.fontFile)[0]
        self.path = Path(normalize_font_path(path))
        numFonts, opener, getSortInfo = getOpener(self.path)
        self.font:BaseFont = opener(self.path, 0)
        self.font._syncLoad()

class Style():
    def RegisterShorthandPrefix(prefix, expansion):
        global _prefixes
        _prefixes.append([prefix, expansion])

    def __init__(self,
            font=None,
            fontSize=12,
            fitHeight=None,
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
            **kwargs):
        """
        kern (k) — a dict of glyphName->[left,right] values in font-space
        tracking (t)
        trackingLimit (tl)
        baselineShift (bs)
        capHeight (ch) — A number in font-space; not specified, read from font; specified as 'x', capHeight is set to xHeight as read from font
        """

        self.font:FontGoggle = font

        self.next = None
        self.layer = layer
        self.layerer = layerer
        self.reverse = kwargs.get("r", reverse)
        self.removeOverlap = kwargs.get("ro", removeOverlap)
        self.rotate = rotate
        
        try:
            os2 = self.font.font.ttFont["OS/2"]
            self.capHeight = os2.sCapHeight
            #self.xHeight = os2.sxHeight
            if capHeight == "x":
                self.capHeight = self.xHeight
        except:
            self.capHeight = 1000 # alternative?

        if capHeight: # override whatever the font says
            if capHeight != "x":
                self.capHeight = capHeight

        if fitHeight:
            self.fontSize = (fitHeight/self.capHeight)*1000
        else:
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

        found_features = features.copy()
        for k, v in kwargs.items():
            if k.startswith("ss") and len(k) == 4:
                found_features[k] = v
            if k in ["dlig", "swsh", "onum", "tnum", "palt"]:
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
        if not self.fontFile == other.fontFile:
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
        self.style = style

        # these will change based on fitting, so we make copies
        self.fontSize = self.style.fontSize
        self.tracking = self.style.tracking
        self.features = self.style.features.copy()
        self.variations = self.style.variations.copy()
        
        self.style = style
        self.glyphs = self.style.font.font.getGlyphRun(self.text, features=self.features, varLocation=self.variations)
        x = 0
        for glyph in self.glyphs:
            glyph.frame = Rect(x+glyph.dx, glyph.dy, glyph.ax, self.style.capHeight)
            x += glyph.ax
    
    def trackFrames(self):
        t = self.tracking
        x_off = 0
        for idx, g in enumerate(self.glyphs):
            g.frame = g.frame.offset(x_off, 0)
            x_off += t
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
        maxw = self.width()
        self.fitField(field, midv)
        midw = self.width()
        self.fitField(field, minv)
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
        self.reset()
        w = self.width()
        if w == width:
            print("VERY RARE")
            return True
        elif w < width: # too small, which means we know it'll fit based on this property
            self.binaryFit(width, field, minv, maxv, 0)
            return True
        else: # too big, so we maintain current value & let the caller know
            return False
    
    def fit(self, width):
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
                self.tracking = self.style.trackingLimit
                if not self.testWidth(width, "tracking", self.style.trackingLimit, 0):
                    if self.style.varyFontSize:
                        self.fontSize = 10
                        if not self.testWidth(width, "fontSize", 10, self.style.fontSize):
                            self.variations["wdth"] = minwdth
                            failed = True
                    else:
                        self.variations["wdth"] = minwdth
                        failed = True
        if failed:
            print("CANT FIT IT >>>", self.text)
        return self

    def shrink(self):
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
        if not adjusted and self.style.next:
            self.setStyle(self.style.next)
            adjusted = True
        if not adjusted and self.style.preventHwid == False and "hwid" not in self.features and not self.style.ufo:
            self.features["hwid"] = True
            self.tracking = self.style.tracking # reset to widest
            self.glyphs = self.hb.glyphs(self.variations, self.features)
            adjusted = True
        return adjusted
    
    def reset(self):
        self.glyphs = self.hb.glyphs(self.variations, self.features)
    
    def formattedString(self, fs=1000):
        if _drawBot:
            feas = dict(self.features)
            del feas["kern"]
            return _drawBot.FormattedString(self.text, font=self.style.fontFile, fontSize=fs, lineHeight=fs+2, fontVariations=self.variations, openTypeFeatures=feas)
        else:
            print("No DrawBot available")
            return None
    
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
        #if self.style.ufo:
        #    shape_reader = UFOShapeReader(self.style)
        #else:
        #    shape_reader = FreetypeReader(self.style)
        #
        #shape_reader.setVariations(self.variations)

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

    def pens(self, frame=True) -> DATPenSet:
        self.style.font.font.addGlyphDrawings(self.glyphs, cocoa=False)
        self.getGlyphFrames()
        pens = DATPenSet()
        for idx, g in enumerate(self.glyphs):
            dp_atom = self._emptyPenWithAttrs()
            rp = g.glyphDrawing.layers[0][0]
            dp_atom.value = self.scalePenToStyle(g, g.glyphDrawing.layers[0][0]).value
            dp_atom.typographic = True
            dp_atom.glyphName = g.name
            
            if False:
                dps = self.drawToPen(dp_atom, self._frames, index=idx)
                if dps:
                    if dps.layered:
                        pens.layered = True
                    dp_atom = dps
                if frame:
                    f.frame.y = 0
                    #if f.frame.y < 0:
                    #    f.frame.y = 0
                    dp_atom.typographic = True
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

    def pen(self, frame=True) -> DATPen:
        dp = self._emptyPenWithAttrs()
        self._frames = self.getGlyphFrames()
        self.drawToPen(dp, self._frames)
        if frame:
            dp.addFrame(Rect((0, 0, self.width(), self.style.capHeight*self.scale())))
            dp.typographic = True
        return dp