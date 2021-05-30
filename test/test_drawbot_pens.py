import unittest
from coldtype.drawbot import *

from PIL import Image
import drawBot as db
import imagehash
import contextlib

renders = Path("test/renders/drawbot")
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
    test.assertEqual(img.exists(), False)

    with new_drawing(rect, save_to=img) as (i, r):
        yield (i, r)
        test.assertEqual(r.w, db.width())
        test.assertEqual(r.h, db.height())
    
    hash_after = hash_img(img)
    test.assertEqual(hash_after, hash_before)
    test.assertEqual(img.exists(), True)

class TestDrawbotPens(unittest.TestCase):
    def test_gs_pen(self):
        with test_image(self, "test_gs_pen.png") as (i, r):
            rr = Rect(0, 0, 100, 100)
            dp = (DraftingPen()
                .define(r=rr, c=75)
                .gs("$r↗ ↘|$c|$r↓ ↙|$c|$r↖")
                .align(r)
                .scale(1.2)
                .f(hsl(0.8, a=0.1))
                .s(hsl(0.9))
                .sw(5)
                .chain(dbdraw))
            self.assertEqual(len(dp.value), 4)
            self.assertEqual(type(dp), DraftingPen)

    def test_distribute_on_path(self):
        mistral = Font.Cacheable("~/Type/fonts/fonts/_script/MistralD.otf")

        with test_image(self, "test_distribute.png", Rect(1000, 1000)) as (i, r):
            s = (StyledString("Hello", Style(mistral, 300))
                .pens()
                .f(hsl(0.3, s=1))
                .align(r)
                .chain(dbdraw))
            
            with db.savedState():
                db.fill(None)
                db.stroke(0)
                db.strokeWidth(1)
                db.rect(*s.ambit())
        
            circle = DraftingPen().oval(r.inset(200)).reverse().rotate(0)
            s2 = (s.copy()
                .zero_translate()
                .distribute_on_path(circle)
                .chain(dbdraw))
            
            self.assertEqual(s.f(), s2.f())


if __name__ == "__main__":
    unittest.main()