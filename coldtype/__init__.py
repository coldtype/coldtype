name = "coldtype"

import math
import os

from collections import OrderedDict
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.pens.boundsPen import ControlBoundsPen, BoundsPen
from fontTools.misc.bezierTools import calcCubicArcLength, splitCubicAtT
from fontTools.ttLib import TTFont
from furniture.geometry import Rect
import unicodedata

from .harfbuzz import Harfbuzz, HarfbuzzFrame
from .freetype import FreetypeReader
from .beziers import CurveCutter


try:
    from booleanOperations.booleanGlyph import BooleanGlyph
    import drawBot as _drawBot
except:
    _drawBot = None


class StyledString():
    def __init__(self,
            text="",
            fontFile=None,
            fontSize=12,
            tracking=0,
            trackingLimit=0,
            space=None,
            variations=dict(),
            variationLimits=dict(),
            increments=dict(),
            features=dict(),
            align="C",
            rect=None,
            drawBot=_drawBot):
        self.text = text
        self.fontFile = os.path.expanduser(fontFile)
        self.ttfont = TTFont(self.fontFile)
        self.harfbuzz = Harfbuzz(self.fontFile)
        self.upem = self.harfbuzz.upem
        #try:
        #    self.upem = self.ttfont["head"].unitsPerEm
        #except:
        #self.upem = 1000
        self.drawBot = _drawBot
        self.fontSize = fontSize
        self.tracking = tracking
        self.trackingLimit = trackingLimit
        self.features = {**dict(kern=True, liga=True), **features}
        self.path = None
        self.offset = (0, 0)
        self.rect = None
        self.increments = increments
        self.space = space
        self.align = align
        self.rect = rect
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
        x_off = 0
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
        return frames
    
    def adjustFramesForPath(self, frames):
        self.tangents = []
        self.limit = len(frames)
        if self.path:
            for idx, f in enumerate(frames):
                ow = f.frame.x+f.frame.w/2
                if ow > self.cutter.length:
                    self.limit = min(idx, self.limit)
                else:
                    p, t = self.cutter.subsegmentPoint(end=ow)
                    f.frame.x = p[0]
                    f.frame.y = f.frame.y + p[1]
                    self.tangents.append(t)
        return frames[0:self.limit]
    
    def getGlyphFrames(self):
        frames = self.harfbuzz.getFrames(text=self.text, axes=self.variations, features=self.features, height=self.ch)
        glyph_names = []
        for f in frames:
            f.frame = f.frame.scale(self.scale())
            glyph_name = self.ttfont.getGlyphName(f.gid)
            code = glyph_name.replace("uni", "")
            #print(glyph_name, f.gid)
            try:
                glyph_names.append(unicodedata.name(chr(int(code, 16))))
            except:
                glyph_names.append(code)
        if ".notdef" in glyph_names:
            pass
            #print("NOTDEF found")
        return self.adjustFramesForPath(self.trackFrames(frames, glyph_names))
    
    def width(self): # size?
        return self.getGlyphFrames()[-1].frame.point("SE").x
    
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
        
        if current_width > width:
            print("DOES NOT FIT", self.tries, self.text)
    
    def place(self, rect):
        self.rect = rect
        self.fit(rect.w)
        x = rect.w/2 - self.width()/2
        self.offset = (0, 0)
        #self.offset = rect.offset(0, rect.h/2 - ch/2).xy()
    
    def addPath(self, path):
        self.path = path
        self.cutter = CurveCutter(path)
    
    def formattedString(self):
        if self.drawBot:
            feas = dict(self.features)
            del feas["kern"]
            return self.drawBot.FormattedString(self.text, font=self.fontFile, fontSize=self.fontSize, lineHeight=self.fontSize+2, tracking=self.tracking, fontVariations=self.variations, openTypeFeatures=feas)
        else:
            print("No DrawBot available")
            return None
    
    def drawToPen(self, out_pen, useTTFont=False):
        fr = FreetypeReader(self.fontFile, ttfont=self.ttfont)
        fr.setVariations(self.variations)
        # self.harfbuzz.setFeatures ???
        self._frames = self.getGlyphFrames()
        
        for idx, frame in enumerate(self._frames):
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
            
    def asRecording(self):
        rp = RecordingPen()
        self.drawToPen(rp)

        if self.rect:
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
            if False:
                with savedState():
                    fill(1, 0, 0.5, 0.5)
                    bp = BezierPath()
                    bp.rect(mnx, mny, mxx-mnx, mxy-mny)
                    bp.translate(xoff, yoff)
                    drawPath(bp)
            diff = self.rect.w - (mxx-mnx)
            rp2 = RecordingPen()
            tp = TransformPen(rp2, (1, 0, 0, 1, xoff, yoff))
            replayRecording(rp.value, tp)
            self._final_offset = (xoff, yoff)
            return rp2
        else:
            return rp

    def asGlyph(self, removeOverlap=False):
        recording = self.asRecording()
        bg = BooleanGlyph()
        replayRecording(recording.value, bg.getPen())
        if removeOverlap:
            bg = bg.removeOverlap()
        return bg
    
    def drawBotDraw(self, removeOverlap=False):
        if self.drawBot:
            g = self.asGlyph(removeOverlap=removeOverlap)
            bp = self.drawBot.BezierPath()
            g.draw(bp)
            self.drawBot.drawPath(bp)
        else:
            print("No DrawBot available")


def flipped_svg_pen(recording, height):
    svg_pen = SVGPathPen(None)
    flip_pen = TransformPen(svg_pen, (1, 0, 0, -1, 0, height))
    #flipped = []
    #for t, pts in recording.value:
    #    flipped.append((t, [(round(x, 1), round(height-y, 1)) for x, y in pts]))
    #replayRecording(flipped, flip_pen)
    replayRecording(recording.value, flip_pen)
    return svg_pen