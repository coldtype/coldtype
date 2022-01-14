import unittest

import coldtype.pens.misc
from coldtype.pens.reportlabpen import ReportLabPen
from coldtype.test import StSt, co, Rect, P, hsl


class TestReportLabPen(unittest.TestCase):
    def test_basic_drawing(self):
        coldtype.pens.misc.USE_SKIA_PATHOPS = False

        r = Rect("letter")
        
        pens = P([
            (P(r.inset(20))
                .align(r)
                .f(0.9)),
            (P(r.inset(40))
                .align(r)
                .fssw(-1, 0, 5)),
            (StSt("COLD", co, 150, wdth=1)
                .align(r)
                .fssw(hsl(0.65, 1, 0.8), hsl(0.9), 2)
                .pen()
                .q2c()
                .removeOverlap())])
        
        self.assertEqual(len(pens[-1].v.value), 117)
        ReportLabPen.PDF(pens, r,
            "test/ignorables/reportlab_test.pdf")
        
        coldtype.pens.misc.USE_SKIA_PATHOPS = True

if __name__ == "__main__":
    unittest.main()