import unittest
from coldtype.pens.cairopen import CairoPen

from pathlib import Path
from coldtype.color import hsl
from coldtype.geometry import Rect
from coldtype.text.composer import StSt, Font
from coldtype.pens.datpen import DATPen, DATPens

from PIL import Image
import drawBot as db
import imagehash
import contextlib

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

renders = Path("test/renders/cairo")
renders.mkdir(parents=True, exist_ok=True)

def hash_img(path):
    if path.exists():
        return (
            imagehash.colorhash(Image.open(path)), 
            imagehash.average_hash(Image.open(path)))
    else:
        return -1

@contextlib.contextmanager
def test_image(test:unittest.TestCase, path, rect=Rect(300, 300)):
    img = (renders / path)
    hash_before = hash_img(img)
    if img.exists():
        img.unlink()

    yield(img, rect)
    
    hash_after = hash_img(img)
    test.assertEqual(hash_after, hash_before)
    test.assertEqual(img.exists(), True)

class TestCairoPen(unittest.TestCase):
    def test_cairo_pdf(self):
        r = Rect(300, 300)
        pdf = renders / "test_cairo.pdf"
        dp = (StSt("CDEL", co, 100, wdth=0.5)
            .pens()
            .align(r))
        CairoPen.Composite(dp, r, pdf)
        self.assertEqual(len(dp), 4)
        self.assertEqual(type(dp), DATPens)
    
    def test_cairo_png(self):
        with test_image(self, "test_cairo.png") as (i, r):
            rr = Rect(0, 0, 100, 100)
            dp = (DATPen()
                .define(r=rr, c=75)
                .gs("$r↗ ↘|$c|$r↓ ↙|$c|$r↖")
                .align(r)
                .scale(1.2)
                .rotate(180)
                .f(hsl(0.5, a=0.1))
                .s(hsl(0.9))
                .sw(5))
            CairoPen.Composite(dp, r, i)
            self.assertEqual(len(dp.value), 4)
            self.assertEqual(type(dp), DATPen)
    
if __name__ == "__main__":
    unittest.main()