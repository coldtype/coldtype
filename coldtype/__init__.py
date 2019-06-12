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

if True:
    sys.path.insert(0, os.path.expanduser("~/Type/furniture"))

from furniture.geometry import Rect

if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath(dirname + "/.."))

from coldtype.beziers import CurveCutter, raise_quadratic, simple_quadratic
from coldtype.svg import SVGContext, flipped_svg_pen

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
        hb.ot_font_set_funcs(font)
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        
        if len(axes.items()) > 0:
            font.set_variations(axes)
        
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
        rp = RecordingPen()
        self.font.glyph.outline.decompose(rp, move_to=FreetypeReader.moveTo, line_to=FreetypeReader.lineTo, conic_to=FreetypeReader.conicTo, cubic_to=FreetypeReader.cubicTo)
        if len(rp.value) > 0:
            rp.closePath()
        replayRecording(rp.value, pen)
        return
    
    def drawTTOutlineToPen(self, pen):
        glyph_name = self.ttfont.getGlyphName(self.glyph_id)
        g = self.ttfont.getGlyphSet()[glyph_name]
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


class StyledString():
    def __init__(self,
            text="",
            font=None,
            fontFile=None,
            fontSize=12,
            tracking=0,
            trackingLimit=0,
            space=None,
            baselineShift=0,
            leftMargin=0,
            rightMargin=0,
            variations=dict(),
            variationLimits=dict(),
            increments=dict(),
            features=dict(),
            align="C",
            rect=None,
            fill=None,
            fallback=None,
            drawBot=_drawBot):
        self.text = text
        self.fontFile = os.path.expanduser((font or fontFile).replace("¬", "~/Library/Fonts"))
        self.ttfont = TTFont(self.fontFile)
        #self.harfbuzz = Harfbuzz(self.fontFile)
        self.fontdata = get_cached_font(self.fontFile)
        self.upem = hb.Face(self.fontdata).upem
        #self.upem = hb.faceself.harfbuzz.upem
        #try:
        #    self.upem = self.ttfont["head"].unitsPerEm
        #except:
        #self.upem = 1000
        self.drawBot = _drawBot
        self.fontSize = fontSize
        self.tracking = tracking
        self.trackingLimit = trackingLimit
        self.baselineShift = baselineShift
        self.leftMargin = leftMargin
        self.rightMargin = rightMargin
        self.features = {**dict(kern=True, liga=True), **features}
        self.path = None
        self.offset = (0, 0)
        self.rect = None
        self.increments = increments
        self.space = space
        self.fallback = fallback
        self.align = align
        self.rect = rect
        self.fill = fill # should normalize?
        
        self.axes = OrderedDict()
        self.variations = dict()
        self.variationLimits = dict()
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
        
        if rect:
            self.place(self.rect)
    
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
            scale = False
        for k, v in variations.items():
            try:
                axis = self.axes[k]
            except KeyError:
                print("Invalid axis", self.fontFile, k)
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
    
    def vowelMark(self, u):
        return "KASRA" in u or "FATHA" in u or "DAMMA" in u or "TATWEEL" in u or "SUKUN" in u
    
    # look away
    def trackFrames(self, frames, glyph_names):
        t = self.tracking*1/self.scale()
        t = self.tracking
        x_off = self.leftMargin
        has_kashida = False
        try:
            self.ttfont.getGlyphID("uni0640")
            has_kashida = True
        except KeyError:
            has_kashida = False
        
        if not has_kashida:
            for idx, f in enumerate(frames):
                gn = glyph_names[idx]
                f.frame = f.frame.offset(x_off, 0)
                x_off += t
                if self.space and gn == "space":
                    x_off += self.space
        else:
            for idx, frame in enumerate(frames):
                frame.frame = frame.frame.offset(x_off, 0)
                try:
                    u = glyph_names[idx]
                    if self.vowelMark(u):
                        continue
                    u_1 = glyph_names[idx+1]
                    if self.vowelMark(u_1):
                        u_1 = glyph_names[idx+2]
                    if "MEDIAL" in u_1 or "INITIAL" in u_1:
                        f = 1.6
                        if "MEEM" in u_1 or "LAM" in u_1:
                            f = 2.7
                        x_off += t*f
                except IndexError:
                    pass
        
        frames[-1].frame.w += self.rightMargin
        return frames
    
    def adjustFramesForPath(self, frames):
        self.tangents = []
        self.originalWidth = 0
        self.limit = len(frames)
        if self.path:
            for idx, f in enumerate(frames):
                ow = f.frame.x+f.frame.w/2
                self.originalWidth = ow
                if ow > self.cutter.length:
                    self.limit = min(idx, self.limit)
                else:
                    p, t = self.cutter.subsegmentPoint(end=ow)
                    x_shift = self.baselineShift * math.cos(math.radians(t))
                    y_shift = self.baselineShift * math.sin(math.radians(t))
                    f.frame.x = p[0] + x_shift
                    f.frame.y = f.frame.y + p[1] + y_shift
                    self.tangents.append(t)
        else:
            for idx, f in enumerate(frames):
                f.frame.y += self.baselineShift
        return frames[0:self.limit]
    
    def getGlyphNames(self, txt):
        frames = Harfbuzz.GetFrames(self.fontdata, text=txt, axes=self.variations, features=self.features, height=self.ch)
        glyph_names = []
        for f in frames:
            glyph_names.append(self.ttfont.getGlyphName(f.gid))
        return glyph_names
    
    def getGlyphFrames(self):
        frames = Harfbuzz.GetFrames(self.fontdata, text=self.text, axes=self.variations, features=self.features, height=self.ch)
        glyph_names = []
        for f in frames:
            f.frame = f.frame.scale(self.scale())
            glyph_name = self.ttfont.getGlyphName(f.gid)
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
        return self.fontSize / self.upem
    
    def fit(self, width):
        _vars = self.variations
        current_width = self.width()
        self.tries = 0
        if current_width > width: # need to shrink
            while self.tries < 1000 and current_width > width:
                if self.tracking > self.trackingLimit:
                    self.tracking -= self.increments.get("tracking", 0.25)
                else:
                    for k, v in self.variationLimits.items():
                        if self.variations[k] > self.variationLimits[k]:
                            self.variations[k] -= self.increments.get(k, 1)
                            break
                self.tries += 1
                current_width = self.width()
        elif current_width < width: # need to expand
            pass
        else:
            return
        
        #print("Fitting", self.text, self.tries, "fits:", current_width <= width)
        #if current_width > width:
        #    print("DOES NOT FIT", self.tries, self.text)
    
    def place(self, rect, fit=True):
        if isinstance(rect, Rect):
            self.rect = rect
        else:
            self.rect = Rect(rect)
        if fit:
            self.fit(self.rect.w)
        x = self.rect.w/2 - self.width()/2
        self.offset = (0, 0)
        #self.offset = rect.offset(0, rect.h/2 - ch/2).xy()
    
    def addPath(self, path, fit=False):
        self.path = path
        self.cutter = CurveCutter(path)
        if fit:
            self.fit(self.cutter.length)
    
    def formattedString(self):
        if self.drawBot:
            feas = dict(self.features)
            del feas["kern"]
            return self.drawBot.FormattedString(self.text, font=self.fontFile, fontSize=self.fontSize, lineHeight=self.fontSize+2, tracking=self.tracking, fontVariations=self.variations, openTypeFeatures=feas)
        else:
            print("No DrawBot available")
            return None
    
    def drawToPen(self, out_pen, frames, useTTFont=False):
        fr = FreetypeReader(self.fontFile, ttfont=self.ttfont)
        fr.setVariations(self.variations)

        for idx, frame in enumerate(frames):
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
    
    def alignedPen(self, rp):
        cbp = ControlBoundsPen(None)
        replayRecording(rp.value, cbp)
        mnx, mny, mxx, mxy = cbp.bounds
        os2 = self.ttfont["OS/2"]
        ch = self.ch * self.scale()
        #if hasattr(os2, "sCapHeight"):
        #    ch = os2.sCapHeight * self.scale()
        #else:
        #    ch = mxy - mny
        y = self.align[0]
        x = self.align[1] if len(self.align) > 1 else "C"
        w = mxx-mnx

        if x == "C":
            xoff = -mnx + self.rect.x + self.rect.w/2 - w/2
        elif x == "W":
            xoff = self.rect.x
        elif x == "E":
            xoff = -mnx + self.rect.x + self.rect.w - w
        
        if y == "C":
            yoff = self.rect.y + self.rect.h/2 - ch/2
        elif y == "N":
            yoff = self.rect.y + self.rect.h - ch
        elif y == "S":
            yoff = self.rect.y
        
        diff = self.rect.w - (mxx-mnx)
        rp2 = RecordingPen()
        tp = TransformPen(rp2, (1, 0, 0, 1, xoff, yoff))
        replayRecording(rp.value, tp)
        self._final_offset = (xoff, yoff)
        return rp2
    
    def roundPen(self, pen, rounding):
        if rounding is None:
            return pen
        else:
            rounded = []
            for t, pts in pen.value:
                rounded.append(
                    (t,
                    [(round(x, rounding), round(y, rounding)) for x, y in pts]))
            pen.value = rounded
            return pen

    def asRecording(self, rounding=None, atomized=False):
        rp = RecordingPen()
        self._frames = self.getGlyphFrames()
        self.drawToPen(rp, self._frames)
        if self.rect and self.align != "SW":
            rp = self.alignedPen(rp)
        
        if hasattr(self, "_final_offset"):
            xoff, yoff = self._final_offset
        else:
            xoff, yoff = 0, 0
        if atomized:
            pens = []
            for f in self._frames:
                frp = RecordingPen()
                self.drawToPen(frp, [f])
                rp2 = RecordingPen()
                tp = TransformPen(rp2, (1, 0, 0, 1, xoff, yoff))
                replayRecording(frp.value, tp)
                # transform
                pens.append(rp2)
            return pens
            #return [self.roundPen(rp, rounding)]
        else:
            return self.roundPen(rp, rounding)

    def asGlyph(self, removeOverlap=False, atomized=False):
        def process(recording):
            bg = BooleanGlyph()
            replayRecording(recording.value, bg.getPen())
            if removeOverlap:
                bg = bg.removeOverlap()
            return bg
        
        if atomized:
            return [process(rec) for rec in self.asRecording(atomized=True)]
        else:
            return process(self.asRecording())
    
    def drawBotDraw(self, removeOverlap=False):
        if self.drawBot:
            g = self.asGlyph(removeOverlap=removeOverlap)
            bp = self.drawBot.BezierPath()
            g.draw(bp)
            self.drawBot.drawPath(bp)
        else:
            print("No DrawBot available")


class StyledStringSetter():
    def __init__(self, strings):
        self.strings = strings
    
    def transform(self, pen, transform):
        op = RecordingPen()
        tp = TransformPen(op, transform)
        replayRecording(pen.value, tp)
        return op
    
    def asRecording(self):
        rp = RecordingPen()
        for pen in self.pens:
            replayRecording(pen.value, rp)
        return rp
    
    def align(self, align="CC", rect=None):
        last_x = 0
        contiguous_pens = []
        contiguous_offsets = []
        for s in self.strings:
            r = s.asRecording()
            contiguous_offsets.append(last_x)
            contiguous_pens.append(self.transform(r, (1, 0, 0, 1, last_x, 0)))
            x, _, w, _ = s._frames[-1].frame
            last_x += x + w
        
        if rect is None:
            self.pens = contiguous_pens
            return contiguous_pens
        else:
            # draw everything into the boundspen
            cbp = ControlBoundsPen(None)
            ch = 0
            for idx, s in enumerate(self.strings):
                os2 = s.ttfont["OS/2"]
                ch = max(ch, s.ch * s.scale())
                replayRecording(contiguous_pens[idx].value, cbp)

            mnx, mny, mxx, mxy = cbp.bounds
            # ch = mxy - mny
            y = align[0]
            x = align[1] if len(align) > 1 else "C"
            w = mxx-mnx

            if x == "C":
                xoff = -mnx + rect.x + rect.w/2 - w/2
            elif x == "W":
                xoff = rect.x
            elif x == "E":
                xoff = -mnx + rect.x + rect.w - w
            
            if y == "C":
                yoff = rect.y + rect.h/2 - ch/2
            elif y == "N":
                yoff = rect.y + rect.h - ch
            elif y == "S":
                yoff = rect.y
            
            diff = rect.w - (mxx-mnx) # for performance-testing

            offset = (xoff, yoff)
            aligned_pens = []
            for idx, s in enumerate(self.strings):
                s.offset = (contiguous_offsets[idx] + xoff, yoff)
                aligned_pens.append(self.transform(contiguous_pens[idx], (1, 0, 0, 1, xoff, yoff)))
            self.pens = aligned_pens
            return aligned_pens


if __name__ == "__main__":
    from furniture.viewer import previewer
    from random import randint

    with previewer() as p:
        pass