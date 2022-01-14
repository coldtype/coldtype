import unittest
from coldtype.geometry import Rect
from coldtype.color import hsl
from coldtype.text.composer import StSt, Font, Style
from coldtype.runon.path import P

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
mutator = Font.Cacheable("assets/MutatorSans.ttf")
r = Rect(1000, 500)

class TestReader(unittest.TestCase):
    def test_fit(self):
        inset = 150
        ri = r.inset(inset, 0)
        out = P([
            P(ri).f(hsl(0.7, a=0.1)),
            (StSt("COLD", co, 500,
                wdth=1, fit=ri.w, _stst=True)
                .fssw(-1, hsl(0.7), 2)
                .align(r))])
        
        self.assertEqual(ri.w, round(out[1].ambit().w))
        self.assertEqual(out[1]._stst.variations["wdth"], 379)
        #out.picklejar(r)
    
    def test_style_mod(self):
        style = Style(co, 250, wdth=1, _stst=True)
        a = StSt("CLDTP", style)
        b = StSt("CLDTP", style.mod(wdth=0))
        
        self.assertEqual(a._stst.variations["wdth"], 1000)
        self.assertEqual(b._stst.variations["wdth"], 0)
    
    def test_fit_height(self):
        style = Style(co, 250, wdth=1, _stst=True)
        a = StSt("CLDTP", style)
        b = StSt("CLDTP", style.mod(fitHeight=300))
        
        self.assertEqual(a._stst.fontSize, 250)
        self.assertEqual(b._stst.fontSize, 400)
    
    def test_kern_pairs(self):
        style = Style(co, 250, wdth=1, _stst=True)
        a = StSt("CLD", style)
        b = StSt("CLD", style.mod(kp={"C/L":20, "L/D":100}))
        
        P([a, b]).fssw(-1, 0, 1).picklejar(r)
        
        self.assertEqual(a[1].ambit().x, 155.75)
        self.assertEqual(b[1].ambit().x, 155.75 + 20*(250/1000))
        self.assertEqual(a[2].ambit().x, 273.5)
        self.assertEqual(b[2].ambit().x, 273.5 + 20*(250/1000) + 100*(250/1000))

if __name__ == "__main__":
    unittest.main()