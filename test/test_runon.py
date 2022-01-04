import re
import unittest
from coldtype.runon.runon import * #INLINE

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
    
    def test_attr(self):
        r = Runon(els=[Runon(1).attr(q=2)])
        
        self.assertEqual(r.attr("q"), None)
        self.assertEqual(r[0].attr("q"), 2)

        r.index(0, lambda p: p.attr(q=3))

        self.assertEqual(r[0].attr("q"), 3)

        r[0].lattr("alt", lambda p2: p2.attr(q=4))
        
        self.assertEqual(r[0].attr("q"), 3)
        self.assertEqual(r[0].attr("alt", "q"), 4)
    
    def test_alpha(self):
        r = Runon(els=[Runon(1).alpha(0.5).tag("leaf")])
        r.alpha(0.5).tag("root")

        alphas = {}
        def walker(el, pos, data):
            if pos >= 0:
                alphas[el.tag()] = data.get("alpha")
        
        r.walk(walker)

        self.assertEqual(alphas["root"], 0.5)
        self.assertEqual(alphas["leaf"], 0.25)
        self.assertEqual(r[0].alpha(), 0.5)
    
    def test_logic(self):
        r = Runon(els=[Runon(1), Runon(2)])

        r.cond(True,
            lambda p: p.data(a="b", c="d"))
        
        r.cond(False,
            lambda p: p,
            lambda p: p.data(x="z"))

        self.assertEqual(r.data("a"), "b")
        self.assertEqual(r.data("c"), "d")
        self.assertEqual(r.data("x"), "z")
    
    def test_layers(self):
        r = Runon(5)

        self.assertEqual(r.v, 5)
        self.assertEqual(len(r), 0)
        self.assertEqual(bool(r), True)
        
        r.layer(2)
        self.assertEqual(r.v, None)
        self.assertEqual(len(r), 2)
        self.assertEqual(len(r[0]), 0)
        self.assertEqual(bool(r), True)

        r.layer(3)
        self.assertEqual(r.v, None)
        self.assertEqual(len(r), 2)
        self.assertEqual(len(r[0]), 3)

        r = Runon(1)
        self.assertEqual(r.v, 1)
        self.assertEqual(r.depth(), 1)
        
        r.layer(lambda p: p.v + 2)
        self.assertEqual(r.v, None)
        self.assertEqual(r[0].v, 3)
        self.assertEqual(r.depth(), 2)
        
        r.layer(lambda p: p.v + 2)
        self.assertEqual(r[0].v, None)
        self.assertEqual(r[0][0].v, 5)
        self.assertEqual(r.depth(), 3)

        r.layer(lambda p: p.v + 2, lambda p: p.v + 3)
        self.assertEqual(r[0][0].v, None)
        self.assertEqual(r[0][0][0].v, 7)
        self.assertEqual(r[0][0][-1].v, 8)
        self.assertEqual(r.depth(), 4)

        r.collapse()
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0].v, 7)
        self.assertEqual(r[-1].v, 8)
    
    def test_chain(self):
        def c(a):
            def _c(ru):
                return ru.update(a)
            return _c

        r = Runon(1)
        self.assertEqual(r.v, 1)
        r.chain(c(5))
        self.assertEqual(r.v, 5)

        r.layer(2)
        r.index(1, lambda e: e.update(e.v*2))
        self.assertEqual(r[0].v, 5)
        self.assertEqual(r[-1].v, 10)

        r.mapv(lambda e: e.update(e.v*2))
        self.assertEqual(r[0].v, 10)
        self.assertEqual(r[-1].v, 20)

        def c2():
            def _c(ru):
                return ru.update(10)
            return _c

        r = Runon(1)
        self.assertEqual(r.v, 1)
        r.chain(c2)
        self.assertEqual(r.v, 10)

        #print("\n")
        #print(r.tree())

if __name__ == "__main__":
    unittest.main()