from fontTools.pens.basePen import BasePen
from furniture.geometry import Rect, Edge, Point
from grapefruit import Color


class PostScriptPen(BasePen):
    def __init__(self, dat):
        BasePen.__init__(self, None)
        self.dat = dat
        self.code = ["newpath"]
        dat.replay(self)

    def _moveTo(self, p):
        self.code.append("{:.02f} {:.02f} moveto".format(*p))

    def _lineTo(self, p):
        self.code.append("{:.02f} {:.02f} rlineto".format(*p))

    def _curveToOne(self, p1, p2, p3):
        self.code.append("{:.02f} {:.02f} curveto".format(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]))

    def _qCurveToOne(self, p1, p2):
        print("NOT SUPPORTED")
        # self.ctx.quad_to(*p1+p2)

    def _closePath(self):
        self.code.append("closepath")
    
    def fill(self, color=None):
        if color:
            self.code.append(self.color(color))
        self.code.append("fill")
        # TODO gradients etc.
    
    def stroke(self, weight=1, color=None):
        if color:
            self.code.append(self.color(color))
        self.code.append("{:.02f} setlinewidth")
        self.code.append("stroke")
    
    def rect(self, rect, t="int"):
        return f"Rectangle<{t}>({t}({rect.x}), {t}({rect.y}), {t}({rect.w}), {t}({rect.h}))"
    
    def color(self, color):
        return "{:.02f} {:.02f} {:.02f} {:.02f} setrgb".format(*color.rgba)
    
    def gradient(self, colors):
        pass
    
    def shadow(self, clip=None, radius=14, alpha=0.3):
        pass

    def image(self, src=None, opacity=1, rect=None):
        pass

    def asCode(self):
        for k, v in self.dat.attrs.items():
            self.code.append("gsave")
            if k == "fill":
                self.fill(v)
            elif k == "stroke":
                self.stroke(**v)
            self.code.append("grestore")
        return "\n".join(self.code)

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.realpath("."))
    from coldtype.pens.datpen import DATPen

    dp1 = DATPen(fill=Color.from_html("deeppink")).rect(Rect((0, 0, 50, 50)))
    ps1 = PostScriptPen(dp1)
    print(ps1.asCode())