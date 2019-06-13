import re
import os
import sys
import math
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.pens.transformPen import TransformPen
from fontTools.ufoLib.glifLib import Glyph

if True:
    sys.path.insert(0, os.path.expanduser("~/Type/furniture"))

from furniture.geometry import Rect


def spinalcase(s):
    return re.sub(r"[A-Z]{1}", lambda c: f"-{c.group().lower()}", s)


def flipped_svg_pen(recording, height):
    svg_pen = SVGPathPen(None)
    flip_pen = TransformPen(svg_pen, (1, 0, 0, -1, 0, height))
    replayRecording(recording.value, flip_pen)
    return svg_pen


def pen_to_svg(recording, rect, **kwargs):
    svg_pen = flipped_svg_pen(recording, rect.h)
    attr_string = " ".join([f"{spinalcase(k)}='{v}'" for k,v in kwargs.items()])
    return f"""
<path {attr_string} d="{svg_pen.getCommands()}"/>
    """


def wrap_svg_paths(paths, rect):
    return f"""
    <svg width="{rect.w}" height="{rect.h}" viewBox="0 0 {rect.w} {rect.h}" xmlns="http://www.w3.org/2000/svg">
        {"".join(paths)}
    </svg>
    """


class SVGContext():
    def __init__(self, w, h):
        self.rect = Rect((0, 0, w, h))
        self.paths = []
    
    def addPath(self, recording, **kwargs):
        svg_path = pen_to_svg(recording, self.rect, **kwargs)
        self.paths.append(svg_path)
    
    def addGlyph(self, glyph, **kwargs):
        try:
            rp = RecordingPen()
            glyph.draw(rp)
            self.addPath(rp, **kwargs)
        except:
            for g in glyph:
                self.addGlyph(g, **kwargs)
            
    
    def addGlyphs(self, glyphs, **kwargs):
        for g in glyphs:
            self.addGlyph(g, **kwargs)
    
    def addRect(self, rect, **kwargs):
        rp = RecordingPen()
        rp.moveTo(rect.point("SW"))
        rp.lineTo(rect.point("NW"))
        rp.lineTo(rect.point("NE"))
        rp.lineTo(rect.point("SE"))
        rp.closePath()
        self.addPath(rp, **kwargs)
    
    def addLine(self, points, **kwargs):
        rp = RecordingPen()
        rp.moveTo(points[0])
        for p in points[1:]:
            rp.lineTo(p)
        self.addPath(rp, **kwargs)
    
    def addRoundedRect(self, rect, hr, vr, **kwargs):
        l, b, w, h = rect
        r, t = l + w, b + h
        K = 4 * (math.sqrt(2)-1) / 3
        if hr <= 0.5:
            hr = w * hr
        if vr <= 0.5:
            vr = h * vr
        rp = RecordingPen()
        rp.moveTo((l + hr, b))
        rp.lineTo((r - hr, b))
        rp.curveTo((r+hr*(K-1), b), (r, b+vr*(1-K)), (r, b+vr))
        rp.lineTo((r, t-vr))
        rp.curveTo((r, t-vr*(1-K)), (r-hr*(1-K), t), (r-hr, t))
        rp.lineTo((l+hr, t))
        rp.curveTo((l+hr*(1-K), t), (l, t-vr*(1-K)), (l, t-vr))
        rp.lineTo((l, b+vr))
        rp.curveTo((l, b+vr*(1-K)), (l+hr*(1-K), b), (l+hr, b))
        rp.closePath()
        self.addPath(rp, **kwargs)
    
    def addOval(self, rect, **kwargs):
        self.addRoundedRect(rect, 0.5, 0.5, **kwargs)

    def toSVG(self):
        return wrap_svg_paths(self.paths, self.rect)


if __name__ == "__main__":
    from furniture.viewer import previewer
    from random import randint

    with previewer() as p:
        svg = SVGContext(1000, 1000)
        svg.addRect(svg.rect.inset(100, 200), fill="deeppink", stroke="royalblue", strokeWidth=10)
        svg.addOval(svg.rect.inset(250, 100), fill="hotpink", stroke="skyblue", strokeWidth=10)
        p.send(svg.toSVG())