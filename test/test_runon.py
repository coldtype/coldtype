import re
import unittest
from coldtype.runon.runon import Runon

class TestRunon(unittest.TestCase):
    def test_init(self):
        r = Runon(1)
        
        self.assertEqual(r.v, 1)

        r = Runon(els=[1])
        
        self.assertEqual(r.v, None)
        self.assertEqual(len(r), 1)

        r = Runon(els=[
            Runon(1), Runon(2)])
        
        self.assertEqual(r.v, None)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0].v, 1)
        self.assertEqual(r[1].v, 2)

        r = Runon(els=[
            Runon(1).data("hi", "word"),
            Runon(2).tag("oy")])
        
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0].data("hi"), "word")
        self.assertEqual(r[1].data("hi"), None)
        self.assertEqual(r[1].tag(), "oy")
        #self.assertEqual(r[2], None)

        self.assertEqual(len(r.find("oy")), 1)
        self.assertEqual(len(r.find_("oy")), 0)
        self.assertEqual(r.find_("oy").tag(), "oy")

        r.mapv(lambda p: p.update(p.v+1))
        
        self.assertEqual(r[0].v, 2)
        self.assertEqual(r[1].v, 3)

        r.filterv(lambda p: p.v == 3)
        
        self.assertEqual(r[0].v, 3)
        self.assertEqual(r[0].tag(), "oy")

        r.insert(0, Runon(4))

        self.assertEqual(r[0].v, 4)
        self.assertEqual(r.sum(), [4, 3])

        self.assertEqual(len(r.find(lambda p: p.v == 3)), 1)
        self.assertEqual(len(r.find(lambda p: p.v == 4)), 1)
        self.assertEqual(len(r.find(lambda p: p.v == 5)), 0)

        r.insert([0, 0], Runon(6))
        r.insert([0, 0], Runon(5))
        self.assertEqual(r[0].sum(), [5, 6])

        r_rev1 = r.copy().reverse(recursive=0)
        r_rev2 = r.copy().reverse(recursive=1)

        self.assertEqual(r_rev1[-1].sum(), [5, 6])
        self.assertEqual(r_rev2[-1].sum(), [6, 5])

        r.insert([0, 0, 0], Runon(10))

        utags = []
        def walker(_, pos, data):
            if pos >= 0:
                utags.append(data.get("utag"))
        
        r.walk(walker)
        
        self.assertEqual(utags,
            ['0_0_0', '0_0', '0_1', '0', '1', None])

        self.assertEqual(r.index(0).v, 4)
        r.index(0, lambda p: p.update(40))
        self.assertEqual(r.index(0).v, 40)

        r.index([0, 0, 0], lambda p: p.update(20))
        self.assertEqual(r.index([0, 0, -1]).v, 20)
        r.index([0, 0, -1], lambda p: p.update(200))
        self.assertEqual(r.index([0, 0, -1]).v, 200)

        els = r.indices([-1, [0, 0, -1]])
        self.assertEqual(len(els), 2)
        self.assertEqual(els[0].v, 3)
        self.assertEqual(els[0].tag(), "oy")
        self.assertEqual(els[1].v, 200)

if __name__ == "__main__":
    unittest.main()