from fontTools.pens.basePen import BasePen
from grapefruit import Color

import sys, os
dirname = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{dirname}/../..")

from coldtype.geometry import Rect, Edge, Point


class PDFPen(BasePen):
    def __init__(self, dat):
        BasePen.__init__(self, None)
        self.dat = dat
        self.code = ["newpath"]
        dat.replay(self)

    def _moveTo(self, p):
        self.code.append("{:.02f} {:.02f} moveto".format(*p))

    def _lineTo(self, p):
        self.code.append("{:.02f} {:.02f} lineto".format(*p))

    def _curveToOne(self, p1, p2, p3):
        self.code.append("{:.02f} {:.02f}  {:.02f} {:.02f}  {:.02f} {:.02f} curveto".format(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]))

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
        self.code.append("{:.02f} setlinewidth".format(weight))
        self.code.append("stroke")
    
    def rect(self, rect, t="int"):
        return f"Rectangle<{t}>({t}({rect.x}), {t}({rect.y}), {t}({rect.w}), {t}({rect.h}))"
    
    def color(self, color):
        return "{:.02f} {:.02f} {:.02f} {:.02f} setrgbcolor".format(*color.rgba)
    
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
    from coldtype.pens.datpen import DATPen
    from coldtype.viewer import viewer
    from random import random

    r = Rect((0, 0, 500, 500))
    dp1 = DATPen(stroke=dict(weight=4, color=Color.from_rgb(random(), random(), random())))
    #dp1.rect(r.inset(100, 100))
    dp1.oval(r.inset(100, 100))
    #dp1.moveTo((50, 50))
    #dp1.lineTo((100, 300))
    #dp1.lineTo(r.point("C"))
    print(r.point("SE"))
    #dp1.oval(r.inset(100, 100))
    ps1 = PostScriptPen(dp1)

    eps = f"""
%!PS-Adobe-3.0 EPSF-3.0
%%Creator: Coldtype
%%Title: Example Title
%%DocumentData: Clean7Bit
%%BeginProlog
%%EndProlog
{ps1.asCode()}
showpage
%%EOF
    """

    p = os.path.realpath("test/artifacts/ps_test.eps")
    with open(p, "w") as f:
        f.write(eps)