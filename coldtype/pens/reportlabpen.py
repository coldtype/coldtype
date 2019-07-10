from fontTools.pens.reportLabPen import ReportLabPen as FTReportLabPen
from reportlab.graphics import renderPM, renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.graphics.shapes import Group, Drawing, scale

if __name__ == "__main__":    
    import os
    import sys
    dirname = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(f"{dirname}/../..")

from coldtype.geometry import Rect, Edge, Point
from coldtype.pens.drawablepen import DrawablePenMixin, Gradient

class ReportLabPen(DrawablePenMixin, FTReportLabPen):
    def __init__(self, dat):
        super().__init__(None, path=None)
        self.dat = dat
    
    def _closePath(self):
        self.path.close()
    
    def fill(self, color):
        if color:
            self.doFill = 1
            self.canvas.setFillColor(self.color(color))
        else:
            self.doFill = 0
    
    def stroke(self, weight=1, color=None):
        if color and weight:
            self.doStroke = 1
            self.canvas.setLineWidth(weight)
            self.canvas.setStrokeColor(self.color(color))
        else:
            self.doStroke = 0
    
    def color(self, color):
        return Color(color.red, color.green, color.blue, alpha=color.alpha)
    
    def draw(self, canvas):
        self.canvas = canvas
        for attr in self.dat.attrs.items():
            self.path = self.canvas.beginPath()
            self.dat.replay(self) # need to do for every attr?
            self.doStroke = 0
            self.doFill = 1
            self.applyDATAttribute(attr)
            self.canvas.drawPath(self.path, stroke=self.doStroke, fill=self.doFill)
    
    def Composite(pens, rect, path):
        c = canvas.Canvas(path, pagesize=(rect.w, rect.h))
        for pen in pens:  
            ReportLabPen(pen).draw(c)
        c.save()
        return c


if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath("."))
    from coldtype.pens.datpen import DATPen, DATPenSet
    from coldtype.viewer import previewer
    from coldtype import StyledString

    if True:
        r = Rect((0, 0, 1920, 1080))
        ss = StyledString("coldtype", "≈/Nonplus-Black.otf", 200)
        dp0 = DATPenSet([dp.addAttrs(fill=(0, 1)) for dp in ss.asDAT(atomized=True, frame=True)])
        dp0.align(r)
        #dp0.removeOverlap()
        dp1 = DATPen(stroke=dict(weight=180, color=("random", 0.5)), fill=("random", 0.5))
        dp1.oval(r.inset(200, 200))
        ReportLabPen.Composite([dp1] + dp0.pens, r, "test/artifacts/test_reportlab.pdf")