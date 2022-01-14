import unittest
from coldtype.pens.skiapen import SkiaPen

from pathlib import Path
from coldtype.color import hsl
from coldtype.geometry import Rect
from coldtype.text.composer import StSt, Font
from coldtype.runon.path import P

from PIL import Image
import imagehash
import contextlib

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

renders = Path("test/renders/skia")
renders.mkdir(parents=True, exist_ok=True)

def hash_img(path):
    if path.exists():
        return (
            imagehash.colorhash(Image.open(path)), 
            imagehash.average_hash(Image.open(path)))
    else:
        return -1

@contextlib.contextmanager
def test_image(test:unittest.TestCase, path, rect=Rect(1000, 500)):
    img = (renders / path)
    hash_before = hash_img(img)
    if img.exists():
        img.unlink()

    yield(img, rect)
    
    hash_after = hash_img(img)
    #test.assertEqual(hash_after, hash_before)
    #test.assertEqual(img.exists(), True)

class TestPensRendered(unittest.TestCase):
    def test_skia_png(self):
        with test_image(self, "test_skia.png") as (i, r):
            dp = ((ß:=P())
                .declare(nx:=100, a:=r.inset(100, 0).subtract(200, "N"))
                .m(a.psw)
                .bxc(a.pn, a.pnw.o(nx, 0), 65)
                .bxc(a.pse, a.pne.o(-nx, 0), 65)
                .ep()
                .fssw(-1, 0, 4)
                .ups()
                .append(StSt("Coldtype Cdelopty".upper(),
                    co, 100, wdth=0.5)
                    .pens()
                    .distribute_on_path(ß[0], center=-5)
                    .f(hsl(0.5)))
                .align(r))
            
            SkiaPen.Precompose(dp, r, disk=str(i))
            self.assertEqual(len(dp), 2)
            self.assertEqual(type(dp), P)
    
if __name__ == "__main__":
    unittest.main()