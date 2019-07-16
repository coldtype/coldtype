import math
import sys
import os
import re

name = "coldtype"
dirname = os.path.dirname(__file__)

from collections import OrderedDict
import freetype
from freetype.raw import *
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.pens.boundsPen import ControlBoundsPen, BoundsPen
from fontTools.ttLib import TTFont
import unicodedata
import uharfbuzz as hb
from itertools import groupby

if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath(dirname + "/.."))

from coldtype.beziers import CurveCutter, raise_quadratic
from coldtype.pens.datpen import DATPen, DATPenSet, Gradient
from coldtype.pens.drawablepen import normalize_color
from coldtype.geometry import Rect, Point

try:
    # relies on undeclared dependencies
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
    def __init__(self, info, position, frame):
        self.gid = info.codepoint
        self.info = info
        self.position = position
        self.frame = frame

    def __repr__(self):
        return f"HarfbuzzFrame: gid{self.gid}@{self.frame}"


class Harfbuzz():
    def GetFrames(fontdata, text="", axes=dict(), features=dict(kern=True, liga=True), height=1000):
        face = hb.Face(fontdata)
        font = hb.Font(face)
        font.scale = (face.upem, face.upem)
        hb.ot_font_set_funcs(font) # necessary?
        if len(axes.items()) > 0:
            font.set_variations(axes)
        
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, features)
        
        infos = buf.glyph_infos
        positions = buf.glyph_positions
        frames = []
        x = 0
        for info, pos in zip(infos, positions):
            gid = info.codepoint
            cluster = info.cluster
            x_advance = pos.x_advance
            x_offset = pos.x_offset
            y_offset = pos.y_offset
            frames.append(HarfbuzzFrame(info, pos, Rect((x+x_offset, y_offset, x_advance, height)))) # 100?
            x += x_advance
        return frames


class FreetypeReader():
    def __init__(self, font_path, ttfont):
        self.fontPath = font_path
        self.font = freetype.Face(font_path)
        self.font.set_char_size(1000)
        #self.scale = scale
        self.ttfont = ttfont
        try:
            self.axesOrder = [a.axisTag for a in self.ttfont['fvar'].axes]
        except:
            self.axesOrder = []
    
    def setVariations(self, axes=dict()):
        if len(self.axesOrder) > 0:
            coords = []
            for name in self.axesOrder:
                coord = FT_Fixed(int(axes[name]) << 16)
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

    def drawOutlineToPen(self, pen, raiseCubics=True):
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
            #pen.lineTo(c3)

    def cubicTo(a, b, c, pen):
        pen.curveTo((a.x, a.y), (b.x, b.y), (c.x, c.y))


def between(c, a, b):
    return ord(a) <= ord(c) <= ord(b)


LATIN = lambda c: between(c, '\u0000', '\u024F')
KATAKANA = lambda c: between(c, '\u30A0', '\u30FF')
HIRAGANA = lambda c: between(c, '\u3040', '\u309F')
CJK = lambda c: between(c, '\u4E00', '\u9FFF')

class Lockup():
    def __init__(self, slugs):
        self.slugs = slugs
    
    def width(self):
        return sum([s.width() for s in self.slugs])
    
    def shrink(self):
        adjusted = False
        for s in self.slugs:
            adjusted = s.shrink() or adjusted
        return adjusted

    def fit(self, width):
        current_width = self.width()
        tries = 0
        if current_width > width: # need to shrink
            while tries < 1000 and current_width > width:
                adjusted = self.shrink()
                for s in self.slugs:
                    adjusted = s.shrink() or adjusted
                if adjusted:
                    tries += 1
                    current_width = self.width()
                else:
                    print(">>> Was not adjusted")
                    return
        elif current_width < width: # need to expand
            pass
        else:
            return
    
    def asPenSet(self):
        # should make things contiguous
        pens = []
        x_off = 0
        for s in self.slugs:
            dps = s.asPenSet()
            dps.translate(x_off, 0)
            pens.extend(dps.pens)
            x_off += dps.frameUnion().w
        return DATPenSet(pens)


class Slug():
    def __init__(self, text, primary, fallback=None):
        self.text = text
        self.primary = primary
        self.fallback = fallback
        self.strings = []
        self.tag()
    
    def tag(self):
        if self.fallback:
            tagged = []
            for c in self.text:
                if LATIN(c) and c != " ":
                    tagged.append(["latin", c])
                else:
                    tagged.append(["other", c])
            
            strings = []
            for k, g in groupby(tagged, lambda e: e[0]):
                txt = "".join([g[1] for g in list(g)])
                if k == "other":
                    strings.append(StyledString(txt, self.primary))
                else:
                    strings.append(StyledString(txt, self.fallback))
            
            self.strings = strings
        else:
            self.strings = [StyledString(self.text, self.primary)]
    
    def width(self):
        return sum([s.width() for s in self.strings])
    
    def shrink(self):
        adjusted = False
        for s in self.strings:
            adjusted = s.shrink() or adjusted
        return adjusted

    def fit(self, width):
        current_width = self.width()
        tries = 0
        if current_width > width: # need to shrink
            while tries < 1000 and current_width > width:
                adjusted = self.shrink()
                if adjusted:
                    tries += 1
                    current_width = self.width()
                else:
                    print(">>> Was not adjusted")
                    return
        elif current_width < width: # need to expand
            pass
        else:
            return

    def asPenSet(self):
        return DATPenSet([s.asPenSet(frame=True) for s in self.strings])
    
    def asPen(self):
        return DATPenSet([s.asPen() for s in self.strings]).asPen()


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
            space=None,
            baselineShift=0,
            xShift=None,
            leftMargin=0,
            rightMargin=0,
            variations=dict(),
            variationLimits=dict(),
            increments=dict(),
            features=dict(),
            varyFontSize=False,
            fill=(0, 0.5, 1),
            stroke=None,
            strokeWidth=1,
            ):
        
        global _prefixes
        ff = font
        for prefix, expansion in _prefixes:
            ff = ff.replace(prefix, expansion)
        
        self.fontFile = os.path.expanduser(ff)
        self.ttfont = ttFont or TTFont(self.fontFile)
        self.fontdata = get_cached_font(self.fontFile)
        self.upem = hb.Face(self.fontdata).upem
        self.fontSize = fontSize
        self.tracking = tracking
        self.trackingLimit = trackingLimit
        self.baselineShift = baselineShift
        self.xShift = xShift
        self.leftMargin = leftMargin
        self.rightMargin = rightMargin
        self.features = {**dict(kern=True, liga=True), **features}
        self.path = None
        self.offset = (0, 0)
        self.increments = increments
        self.space = space

        self.fill = normalize_color(fill)
        self.stroke = normalize_color(stroke)
        self.strokeWidth = strokeWidth

        self.axes = OrderedDict()
        self.variations = dict()
        self.variationLimits = dict()
        self.varyFontSize = varyFontSize
        try:
            fvar = self.ttfont['fvar']
        except KeyError:
            fvar = None
        if fvar:
            for axis in fvar.axes:
                self.axes[axis.axisTag] = axis
                self.variations[axis.axisTag] = axis.defaultValue
                if axis.axisTag == "wdth": # the only reasonable default
                    self.variationLimits[axis.axisTag] = axis.minValue

        self.addVariations(variations)
        
        os2 = self.ttfont["OS/2"]
        if hasattr(os2, "sCapHeight"):
            self.ch = os2.sCapHeight
        else:
            self.ch = 1000 # alternative?
    
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
                variations[k] = int((axis.maxValue-axis.minValue)*v + axis.minValue)
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


class StyledString():
    def __init__(self, text, style):
        self.text = text
        self.style = style
        
        self.path = None
        self.offset = (0, 0)

        # these will change based on fitting, so we make copies
        self.fontSize = self.style.fontSize
        self.tracking = self.style.tracking
        self.features = self.style.features.copy()
        self.variations = self.style.variations.copy()
    
    # look away
    def trackFrames(self, frames, glyph_names):
        t = self.tracking
        x_off = self.style.leftMargin
        # has_kashida = False
        # try:
        #     self.style.ttfont.getGlyphID("uni0640")
        #     has_kashida = True
        # except KeyError:
        #     has_kashida = False
        
        for idx, f in enumerate(frames):
            gn = glyph_names[idx]
            f.frame = f.frame.offset(x_off, 0)
            x_off += t
            if self.style.space and gn.lower() == "space":
                x_off += self.style.space
        
        frames[-1].frame.w += self.style.rightMargin
        return frames
    
    def adjustFramesForPath(self, frames):
        self.limit = len(frames)
        if self.path:
            self.tangents = []
            self.originalWidth = 0
            for idx, f in enumerate(frames):
                try:
                    bs = self.style.baselineShift[idx]
                except:
                    bs = self.style.baselineShift
                
                ow = f.frame.x+f.frame.w/2
                self.originalWidth = ow
                if ow > self.cutter.length:
                    self.limit = min(idx, self.limit)
                else:
                    p, t = self.cutter.subsegmentPoint(end=ow)
                    x_shift = bs * math.cos(math.radians(t))
                    y_shift = bs * math.sin(math.radians(t))
                    f.frame.x = p[0] + x_shift
                    f.frame.y = f.frame.y + p[1] + y_shift
                    self.tangents.append(t)
        else:
            for idx, f in enumerate(frames):
                try:
                    bs = self.style.baselineShift[idx]
                except:
                    bs = self.style.baselineShift
                f.frame.y += bs
                if self.style.xShift:
                    try:
                        f.frame.x += self.style.xShift[idx]
                    except:
                        pass
        return frames[0:self.limit]
    
    def getGlyphNames(self, txt):
        frames = Harfbuzz.GetFrames(self.style.fontdata, text=txt, axes=self.variations, features=self.features, height=self.style.ch)
        glyph_names = []
        for f in frames:
            glyph_names.append(self.style.ttfont.getGlyphName(f.gid))
        return glyph_names
    
    def getGlyphFrames(self):
        frames = Harfbuzz.GetFrames(self.style.fontdata, text=self.text, axes=self.variations, features=self.features, height=self.style.ch)
        glyph_names = []
        for f in frames:
            f.frame = f.frame.scale(self.scale())
            glyph_name = self.style.ttfont.getGlyphName(f.gid)
            code = glyph_name.replace("uni", "")
            try:
                glyph_names.append(unicodedata.name(chr(int(code, 16))))
            except:
                glyph_names.append(code)
        self.glyphNames = glyph_names
        return self.adjustFramesForPath(self.trackFrames(frames, glyph_names))
    
    def width(self): # size?
        fw = self.getGlyphFrames()[-1].frame.point("SE").x
        if hasattr(self, "originalWidth"):
            return max(fw, self.originalWidth)
        else:
            return fw
    
    def scale(self):
        return self.fontSize / self.style.upem
    
    def shrink(self):
        adjusted = False
        if self.tracking > 0:
            self.tracking -= self.increments.get("tracking", 0.25)
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
        if not adjusted and "hwid" not in self.features:
            #print("HWID'ing")
            self.features["hwid"] = True
            adjusted = True
        return adjusted
    
    def fit(self, width):
        current_width = self.width()
        self.tries = 0
        if current_width > width: # need to shrink
            while self.tries < 1000 and current_width > width:
                adjusted = self.shrink()
                if adjusted:
                    self.tries += 1
                    current_width = self.width()
                else:
                    #print(">>> Was not adjusted")
                    return
        elif current_width < width: # need to expand
            pass
        else:
            return        
        #print("Fitting", self.text, self.tries, "fits:", current_width <= width)
        #if current_width > width:
        #    print("DOES NOT FIT", self.tries, self.text)
    
    def addPath(self, path, fit=False):
        self.path = path
        self.cutter = CurveCutter(path)
        if fit:
            self.fit(self.cutter.length)
    
    def formattedString(self):
        if _drawBot:
            feas = dict(self.features)
            del feas["kern"]
            return _drawBot.FormattedString(self.text, font=self.fontFile, fontSize=self.fontSize, lineHeight=self.fontSize+2, tracking=self.tracking, fontVariations=self.variations, openTypeFeatures=feas)
        else:
            print("No DrawBot available")
            return None
    
    def drawToPen(self, out_pen, frames, index=None, useTTFont=False):
        fr = FreetypeReader(self.style.fontFile, ttfont=self.style.ttfont)
        fr.setVariations(self.variations)

        for idx, frame in enumerate(frames):
            if index is not None and idx != index:
                continue
            fr.setGlyph(frame.gid)
            s = self.scale()
            t = Transform()
            t = t.scale(s)
            t = t.translate(frame.frame.x/self.scale(), frame.frame.y/self.scale())
            if self.path:
                tangent = self.tangents[idx]
                t = t.rotate(math.radians(tangent-90))
                t = t.translate(-frame.frame.w*0.5/self.scale())
            #print(self.offset)
            t = t.translate(self.offset[0]/self.scale(), self.offset[1]/self.scale())
            tp = TransformPen(out_pen, (t[0], t[1], t[2], t[3], t[4], t[5]))
            if useTTFont:
                fr.drawTTOutlineToPen(tp)
            else:
                fr.drawOutlineToPen(tp, raiseCubics=True)
    
    def _emptyPenWithAttrs(self):
        return DATPen(fill=self.style.fill, stroke=dict(color=self.style.stroke, weight=self.style.strokeWidth))

    def asPenSet(self, frame=True):
        self._frames = self.getGlyphFrames()
        pens = []
        for idx, f in enumerate(self._frames):
            #print(f.frame)
            dp_atom = self._emptyPenWithAttrs()
            self.drawToPen(dp_atom, self._frames, index=idx)
            if frame:
                dp_atom.addFrame(f.frame)
            pens.append(dp_atom)
        return DATPenSet(pens)

    def asPen(self, frame=True):
        dp = self._emptyPenWithAttrs()
        self._frames = self.getGlyphFrames()
        self.drawToPen(dp, self._frames)
        if frame:
            dp.addFrame(Rect((0, 0, self.width(), self.style.ch*self.scale())))
            dp.typographic = True
        return dp


if __name__ == "__main__":
    from grapefruit import Color
    from coldtype.viewer import previewer
    from random import randint
    from coldtype.pens.svgpen import SVGPen

    def map_test(preview):
        f, v = ["¬/Fit-Variable.ttf", dict(wdth=0.2, scale=True)]
        f, v = ["¬/Cheee_Variable.ttf", dict(yest=1, grvt=0.95, temp=0.4, scale=True)]
        #f, v = ["≈/MapRomanVariable-VF.ttf", dict(wdth=0, scale=True)]

        rect = Rect(0, 0, 1000, 1000)
        def make_ss(shift):
            return StyledString("California",
                Style(font=f,
                variations=v,
                fontSize=170,
                tracking=-10,
                baselineShift=shift))
        ss1 = make_ss(-19)
        ss2 = make_ss(-32)
        ss3 = make_ss(-8)
        r = rect.inset(50, 30).offset(200, 0)
        rp = simple_quadratic(r.p("NW"), r.p("W").offset(0, -100), r.p("S").offset(100, 0))
        ss1.addPath(rp, fit=True)
        ss2.addPath(rp, fit=True)
        ss3.addPath(rp, fit=True)
        dp1 = ss1.asPen().addAttrs(fill=Gradient.Horizontal(r, "orange", "deeppink"), stroke=dict(color="white", weight=2))
        dp1.removeOverlap()
        dp2 = ss2.asPen().addAttrs(fill=("black", 0.5), stroke=("white", 0.3))
        dp2.removeOverlap()
        dp3 = ss3.asPen().addAttrs(fill=("deeppink", 0.5), stroke=("white", 0.3))
        dp3.removeOverlap()
        preview.send(SVGPen.Composite([DATPen(fill=Gradient.Vertical(rect, "darkorchid", "royalblue")).rect(rect), dp2, dp1], rect), rect)
    
    def ss_bounds_test(font, preview):
        #f = f"≈/{font}.ttf"
        f = font
        r = Rect((0, 0, 700, 120))
        ss = StyledString("ABC", font=f, fontSize=100, variations=dict(wght=1, wdth=1,  scale=True), features=dict(ss01=True))
        dp = ss.asPen()
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
        r = Rect((0, 0, 500, 500))
        f, v = ["≈/VulfSansItalicVariable.ttf", dict(wght=1, scale=True)]
        f, v = ["≈/Nonplus-Black.otf", dict()]
        ss1 = StyledString("Yoy! ", Style(font=f, variations=v, fontSize=80))
        f, v = ["¬/Fit-Variable.ttf", dict(wdth=0.1, scale=True)]
        ss2 = StyledString("ABC", Style(font=f, variations=v, fontSize=120))
        grid = r.inset(0, 0).grid(10, 10)
        dp1 = DATPen(fill=None, stroke=dict(color=("skyblue", 0.5), weight=1)).rect(grid)
        oval = DATPen()
        #oval.polygon(15, Rect(0, 0, 50, 50)).addAttrs(fill="random")
        oval.polygon(3, Rect(0, 0, 50, 50)).addAttrs(fill="random")
        oval.addFrame(Rect(0, 0, 50, 50).expand(40, "minx"))
        oval.typographic = True
        dps = DATPenSet(ss1.asPen(frame=True).addAttrs(fill="darkorchid"), ss2.asPen(frame=True), oval)
        #dps = DATPenSet(DATPen().rect(Rect((0, 0, 100, 200))), DATPen().oval(Rect((0, 0, 500, 200))))
        #dps.align(grid)
        dps.align(r, x="centerx", y="centery", typographicBaseline=True)
        preview.send(SVGPen.Composite(dps.pens + [dp1], r), r)

    def rotalic_test(preview):
        r = Rect(0, 0, 500, 500)
        s = Slug("Side", Style("≈/Vinila-VF-HVAR-table.ttf", 200, variations=dict(wdth=0.5, wght=0.7, scale=True)))
        dps = s.asPenSet(atomized=True)
        for dp in dps.pens:
            dp.rotate(-15)
        dps.align(r)
        preview.send(SVGPen.Composite(dps.pens, r), r)

    def multilang_test(p):
        ss = Lockup([
            Slug(
                #"الملخبط",
                "Ali الملخبط Boba",
                Style("≈/GretaArabicCondensedAR-Heavy.otf", 100),
                Style("≈/ObviouslyVariable.ttf", 100, variations=dict(wdth=1, wght=1))
            )])
        r = Rect((0, 0, 500, 500))
        ss.fit(r.w - 20)
        dps = ss.asPenSet()
        dps.align(r)
        p.send(SVGPen.Composite(dps.pens, r), r)
    
    def tracking_test(p):
        r = Rect(0, 0, 500, 200)
        s1 = Slug("ABC", Style("≈/VulfSans-Black.otf", 100, tracking=50, fill=("random", 0.2), strokeWidth=2, stroke=("random", 0.5)))
        s2 = Slug("xyz", Style("≈/VulfSans-Black.otf", 100, fill=("random", 0.1), strokeWidth=2, stroke=("random", 0.5)))
        ps1 = s1.asPenSet()
        ps1.align(r)
        ps2 = s2.asPenSet()
        ps2.align(r)
        frames = []
        #for pen in ps1.pens:
        #    frames.append(DATPen(fill=("random", 0.5)).rect(pen.frame))
        p.send(SVGPen.Composite(frames + ps1.pens + ps2.pens + [DATPen.Grid(r, x=6, y=8)], r), r)

    with previewer() as p:
        if False:
            ss_bounds_test("≈/ObviouslyVariable.ttf", p)
            #ss_bounds_test("≈/MutatorSans.ttf", p)
            ss_bounds_test("≈/VinilaVariable.ttf", p)
            ss_bounds_test("≈/Vinila-VF-HVAR-table.ttf", p)
            #ss_bounds_test("≈/Compressa-MICRO-GX-Rg.ttf", p)
            #ss_bounds_test("≈/BildVariableV2-VF.ttf", p)
            #ss_bounds_test("≈/BruphyGX.ttf", p)
            #ss_bounds_test("≈/Fit-Variable.ttf", p)
            #ss_bounds_test("≈/MapRomanVariable-VF.ttf", p)
            #ss_bounds_test("≈/VulfSansItalicVariable.ttf", p)
        #ss_and_shape_test(p)
        #map_test(p)
        #rotalic_test(p)
        #multilang_test(p)
        tracking_test(p)