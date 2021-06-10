import unittest

import coldtype.pens.misc
from coldtype.pens.reportlabpen import ReportLabPen
from coldtype.test import StSt, co, Rect, DP, DPS, hsl


class TestReportLabPen(unittest.TestCase):
    def test_basic_drawing(self):
        coldtype.pens.misc.USE_SKIA_PATHOPS = False
        r = Rect("letter")
        pens = DPS([
            (DP(r.inset(20))
                .align(r)
                .f(0.9)),
            (DP(r.inset(40))
                .align(r)
                .f(None)
                .s(0).sw(5)),
            (StSt("COLD", co, 150, wdth=1)
                .align(r)
                .f(hsl(0.3))
                .s(hsl(0.9))
                .sw(5)
                .pen()
                .q2c()
                .removeOverlap()
                )])
        
        self.assertEqual(len(pens[-1].value), 117)
        ReportLabPen.PDF(pens, r,
            "test/ignorables/reportlab_test.pdf")
        coldtype.pens.misc.USE_SKIA_PATHOPS = True

if __name__ == "__main__":
    unittest.main()