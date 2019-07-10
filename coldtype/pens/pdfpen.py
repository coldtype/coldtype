from fontTools.pens.basePen import BasePen
from grapefruit import Color

import sys, os
dirname = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{dirname}/../..")

from coldtype.geometry import Rect, Edge, Point

pdf_template = """
%PDF-1.3
%����
1 0 obj 
<<
/pdftk_PageNum 1
/Resources 2 0 R
/Contents 3 0 R
/Parent 4 0 R
/Type /Page
/MediaBox [0 0 {:d} {:d}]
>>
endobj 
4 0 obj 
<<
/Kids [1 0 R]
/Type /Pages
/MediaBox [0 0 {:d} {:d}]
/Count 1
>>
endobj 
3 0 obj 
<<
/Length {:d}
>>
stream
{:s}
endstream 
endobj 
2 0 obj 
<<
/ProcSet [/PDF]
/ExtGState 
<<
/Gs1 5 0 R
>>
/ColorSpace 
<<
/Cs1 6 0 R
>>
>>
endobj 
6 0 obj [/ICCBased 7 0 R]
endobj 
5 0 obj 
<<
/ca 0.1
/Type /ExtGState
>>
endobj 
7 0 obj 
<<
/N 3
/Length 2008
/Alternate /DeviceRGB
>>
stream
endstream 
endobj 
8 0 obj 
<<
/Type /Catalog
/Version /1.4
/Pages 4 0 R
>>
endobj 
9 0 obj (Mac OS X 10.13.6 Quartz PDFContext)
endobj 
10 0 obj (D:20190710220425Z00'00')
endobj 
11 0 obj 
<<
/ModDate (D:20190710220425Z00'00')
/CreationDate (D:20190710220425Z00'00')
/Producer (Mac OS X 10.13.6 Quartz PDFContext)
>>
endobj xref
0 12
0000000000 65535 f 
0000000015 00000 n 
0000000646 00000 n 
0000000225 00000 n 
0000000140 00000 n 
0000000778 00000 n 
0000000744 00000 n 
0000000826 00000 n 
0000002916 00000 n 
0000002981 00000 n 
0000003034 00000 n 
0000003077 00000 n 
trailer

<<
/Info 11 0 R
/ID [<cf76d9d64ba6bbf325ed905cf3fe5411> <cf76d9d64ba6bbf325ed905cf3fe5411>]
/Root 8 0 R
/Size 12
>>
startxref
3222
%%EOF
"""


class PDFPen(BasePen):
    def __init__(self, dat):
        BasePen.__init__(self, None)
        self.dat = dat

        self.code = ["q /Cs1 cs"]
        for k, v in self.dat.attrs.items():
            if k == "fill":
                self.code.append(self.color(v, "rg"))
        dat.replay(self)
        for k, v in self.dat.attrs.items():
            if k == "fill":
                self.code.append("f")
        self.code += ["Q"]

    def _moveTo(self, p):
        self.code.append("{:.02f} {:.02f} m".format(*p))

    def _lineTo(self, p):
        self.code.append("{:.02f} {:.02f} l".format(*p))

    def _curveToOne(self, p1, p2, p3):
        self.code.append("{:.02f} {:.02f}  {:.02f} {:.02f}  {:.02f} {:.02f} c".format(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]))

    def _qCurveToOne(self, p1, p2):
        print("NOT SUPPORTED")
        # self.ctx.quad_to(*p1+p2)

    def _closePath(self):
        self.code.append("h")
    
    def fill(self, color=None):
        if color:
            self.code.append(self.color(color, "rg"))
        self.code.append("f")
        # TODO gradients etc.
    
    def stroke(self, weight=1, color=None):
        if color:
            self.code.append(self.color(color, "RG"))
        self.code.append("{:.02f} setlinewidth".format(weight))
        self.code.append("s")
    
    def color(self, color, op):
        return "{:.02f} {:.02f} {:.02f} {:s}".format(*color.rgb, op) # TODO alpha
    
    def gradient(self, colors):
        pass
    
    def shadow(self, clip=None, radius=14, alpha=0.3):
        pass

    def image(self, src=None, opacity=1, rect=None):
        pass
        #return "\n".join(self.code)

if __name__ == "__main__":
    from coldtype.pens.datpen import DATPen
    from coldtype.viewer import viewer
    from random import random

    r = Rect((0, 0, 1920, 1080))
    dp1 = DATPen(fill="random")
    dp1.oval(r.inset(100, 100)).translate(0, 0)
    pp = PDFPen(dp1)
    nc = " ".join(pp.code)
    pdf = pdf_template.format(r.w, r.h, r.w, r.h, len(nc) + 100, nc)

    with open("test_gen.pdf", "w") as f:
        f.write(pdf)

    #p = os.path.realpath("test/artifacts/fpdf_test.pdf")