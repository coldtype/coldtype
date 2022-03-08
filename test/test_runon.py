import unittest
from coldtype.runon.runon import * #INLINE

class TestRunon(unittest.TestCase):
    def test_init(self):
        r = Runon(1)
        
        self.assertEqual(r.v, 1)

        r = Runon(Runon(1))
        
        self.assertEqual(r.v, None)
        self.assertEqual(len(r), 1)

        r = Runon(Runon(1), Runon(2))
        
        self.assertEqual(r.v, None)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0].v, 1)
        self.assertEqual(r[1].v, 2)

        r = Runon([Runon(1), Runon(2)])
        
        self.assertEqual(r.v, None)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0].v, 1)
        self.assertEqual(r[1].v, 2)

        r = Runon(3, 2, 1)
        
        self.assertEqual(len(r), 3)
        self.assertEqual(r[0].v, 3)
        self.assertEqual(r[-1].v, 1)

        r.reverse()

        self.assertEqual(r[0].v, 1)
        self.assertEqual(r[-1].v, 3)

        r = Runon(
            Runon(1).data(hi="word"),
            Runon(2).tag("oy"))
        
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
        self.assertEqual(r[0].sum(), [4, 5, 6])

        r.data(hello="world")
        r.index([0, 0], lambda e: e.attr(fill=1))

        r_copy = r.copy()

        self.assertEqual(r_copy[0][0].attr("fill"), 1)

        r.index([0, 0], lambda e: e.attr(fill=2))
        r_copy.index([0, 0], lambda e: e.attr(fill=3))

        self.assertEqual(r[0][0].attr("fill"), 2)
        self.assertEqual(r_copy[0][0].attr("fill"), 3)

        self.assertEqual(r_copy.data("hello"), "world")
        self.assertEqual(r_copy[-1].tag(), "oy")

        r_rev1 = r.copy().reverse(recursive=0)
        r_rev2 = r.copy().reverse(recursive=1)

        self.assertEqual(r_rev1[-1].sum(), [4, 5, 6])
        self.assertEqual(r_rev2[-1].sum(), [4, 6, 5])

        r.insert([0, 0, 0], Runon(10))

        utags = []
        def walker(_, pos, data):
            if pos >= 0:
                utags.append(data.get("utag"))
        
        r.walk(walker)
        
        self.assertEqual(utags,
            ['0_0_0', '0_0', '0_1', '0', '1', 'ROOT'])

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

        r = Runon(1)
        utags = []
        r.walk(walker)
        self.assertEqual(utags, ["ROOT"])
    
    def test_attr(self):
        r = Runon(Runon(1).attr(q=2))
        
        self.assertEqual(r.attr("q"), None)
        self.assertEqual(r[0].attr("q"), 2)

        r.index(0, lambda p: p.attr(q=3))

        self.assertEqual(r[0].attr("q"), 3)

        r[0].lattr("alt", lambda p2: p2.attr(q=4))
        
        self.assertEqual(r[0].attr("q"), 3)
        self.assertEqual(r[0].attr("alt", "q"), 4)
    
    def test_alpha(self):
        r = Runon(Runon(1).alpha(0.5).tag("leaf"))
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
        r = Runon(Runon(1), Runon(2))

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
        r.layer(3)
        self.assertEqual(len(r), 3)
        
        r.layer(2)
        self.assertEqual(len(r), 2)
        self.assertEqual(len(r[0]), 3)

        r = Runon(5)

        self.assertEqual(r.v, 5)
        self.assertEqual(len(r), 0)
        self.assertEqual(bool(r), True)
        
        r.layerv(2)
        self.assertEqual(r.v, None)
        self.assertEqual(len(r), 2)
        self.assertEqual(len(r[0]), 0)
        self.assertEqual(bool(r), True)

        r.layerv(3)
        self.assertEqual(r.v, None)
        self.assertEqual(len(r), 2)
        self.assertEqual(len(r[0]), 3)

        r = Runon(1)
        self.assertEqual(r.v, 1)
        self.assertEqual(r.depth(), 0)
        
        r.layerv(lambda p: p.v + 2)
        self.assertEqual(r.v, None)
        self.assertEqual(r[0].v, 3)
        self.assertEqual(r.depth(), 1)
        
        r.layerv(lambda p: p.v + 2)
        self.assertEqual(r[0].v, None)
        self.assertEqual(r[0][0].v, 5)
        self.assertEqual(r.depth(), 2)

        r.layerv(lambda p: p.v + 2, lambda p: p.v + 3)
        self.assertEqual(r[0][0].v, None)
        self.assertEqual(r[0][0][0].v, 7)
        self.assertEqual(r[0][0][-1].v, 8)
        self.assertEqual(r.depth(), 3)

        r.collapse()
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0].v, 7)
        self.assertEqual(r[-1].v, 8)

        r = Runon(1, 2, 3)
        r[0].data(hello="world")
        r.layerv(1, lambda e: e.update(e.v+1))
        self.assertEqual(r[0].data("hello"), None)

        r = Runon(1)
        
        r.ups()
        self.assertEqual(r[0].v, 1)
        
        r.ups()
        self.assertEqual(r[0].v, None)
        self.assertEqual(r[0][0].v, 1)
        
        r.ups()
        r.insert(0, Runon(2))
        self.assertEqual(r[0].v, 2)
        self.assertEqual(r[1][0].v, None)
        self.assertEqual(r[1][0][0].v, 1)
        
        r.ups()
        self.assertEqual(len(r), 1)
        self.assertEqual(len(r[0]), 2)
    
    def test_collapse(self):
        r = Runon(Runon(Runon(1, 2), 3), Runon(4, 5))
        r.collapse()
        self.assertEqual(r.sum(), [1, 2, 3, 4, 5])
        
        r.reverse()
        self.assertEqual(r.sum(), [5, 4, 3, 2, 1])
        
        r = Runon(Runon(1, 2, 3), Runon(4, 5, 6))
        r.collapse()
        self.assertEqual(r.sum(), [1, 2, 3, 4, 5, 6])
    
    def test_chain(self):
        def c(a):
            def _c(ru):
                return ru.update(a)
            return _c

        r = Runon(1)
        self.assertEqual(r.v, 1)
        r.chain(c(5))
        self.assertEqual(r.v, 5)

        r.layerv(2)
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

        # variant syntax

        r = Runon(1, 2, 3)
        r / (lambda p: p.update(p.v+1))
        self.assertEqual(r.sum(), [2, 3, 4])

        def ch(a):
            def _ch(ro):
                ro / (lambda p: p.update(p.v + a))
            return _ch

        r = Runon(1, 2, 3)
        r | ch(2)
        self.assertEqual(r.sum(), [3, 4, 5])

        r = Runon(1, 2, 3)
        r - ch(2)
        self.assertEqual(r.sum(), [1, 2, 3])
    
    def test_inter(self):
        r = Runon(1, 2, 3)
        self.assertEqual(len(r), 3)
        
        r.interpose(Runon(10))
        self.assertEqual(len(r), 5)

        r = Runon(1, 2, 3)
        self.assertEqual(len(r), 3)
        self.assertEqual(len(r[0]), 0)

        r.layerv(1, lambda e: e.update(e.v+1))
        self.assertEqual(len(r), 3)
        self.assertEqual(len(r[0]), 2)
        self.assertEqual(r[0][0].v, 1)
        self.assertEqual(r[0][1].v, 2)

        r = Runon(3, 2, 1)
        r.split(2)
        self.assertEqual(len(r), 2)
        self.assertEqual(r.sum(), [3, 1])
        
        r = Runon(1, 2, 3)
        r.split(lambda e: e.v == 2)
        self.assertEqual(len(r), 2)
        self.assertEqual(len(r[0]), 1)
        self.assertEqual(len(r[1]), 1)
        self.assertEqual(r.sum(), [1, 3])

        r = Runon(1, 2, 3)
        r.split(lambda e: e.v == 2, -1)
        self.assertEqual(len(r), 2)
        self.assertEqual(len(r[0]), 2)
        self.assertEqual(len(r[1]), 1)
        self.assertEqual(r.sum(), [1, 2, 3])

        r = Runon(1, 2, 3)
        r.split(lambda e: e.v == 2, 1)
        self.assertEqual(len(r), 2)
        self.assertEqual(len(r[0]), 1)
        self.assertEqual(len(r[1]), 2)
        self.assertEqual(r.sum(), [1, 2, 3])
    
    def test_enumerate(self):
        r = Runon().enumerate(range(0, 5), lambda en: Runon((en.el+1)*10))
        self.assertEqual(r.sum(), [10, 20, 30, 40, 50])

        r = Runon().enumerate(range(0, 5), lambda en: Runon(en.e))
        self.assertEqual(r.sum(), [0, 0.25, 0.5, 0.75, 1])

        r = Runon().enumerate(zip(["A", "B", "C"], [1, 2, 3]), lambda en:
            Runon(f"{en.el[0]}{en.el[1]}"))
        
        self.assertEqual(r[0].v, "A1")
        self.assertEqual(r[-1].v, "C3")
    
    def test_add(self):
        r = Runon(1, 2, 3)
        r += Runon(4)
        self.assertEqual(r.sum(), [1, 2, 3, 4])

        r = Runon(1, 2, 3)
        r2 = r + 4
        self.assertEqual(r.sum(), [1, 2, 3])
        self.assertEqual(r2.sum(), [1, 2, 3, 4])
        self.assertEqual(r2[0].sum(), [1, 2, 3])
        self.assertEqual(r2[1].sum(), [4, 4])
    
    def test_index(self):
        r = Runon(1, 2, 3)
        r.index(0, lambda e: e.tag("one"))
        self.assertEqual(r[0].tag(), "one")
    
    def test_find(self):
        r = Runon(Runon(1, 2), Runon(1, 2, 3))
        r.index([0, 1], lambda e: e.tag("alpha"))
        r.index([1, 1], lambda e: e.tag("beta"))

        self.assertEqual(
            r.find_(lambda e: e.v == 2).tag(),
            "alpha")
        
        self.assertEqual(
            r.find_(lambda e: e.v == 2, index=1).tag(),
            "beta")
    
    def test_append_insert(self):
        # should normalize and ignore None

        r = Runon(1, 2, 3)
        r.insert(0, 10)
        self.assertEqual(r[0].v, 10)

        r.insert(0, None)
        self.assertEqual(r[0].v, 10)

        self.assertEqual(r[-1].v, 3)
        r.append(None)
        self.assertEqual(r[-1].v, 3)

        r += None
        self.assertEqual(r[-1].v, 3)

        r = Runon(1, 2, 3, None)
        self.assertEqual(len(r), 3)
        self.assertEqual(r[-1].v, 3)

        r = Runon(1, 2, 3, Runon(None))
        self.assertEqual(len(r), 4)
        self.assertEqual(r[-1].v, None)
    
    def test_tree(self):
        r = Runon(1, 2, Runon(11, Runon(21, 22), 13), 3)
        
        rt1 = r.tree().split("\n")
        self.assertTrue(" | | - <®::int(22)>" in rt1)
        self.assertEqual(len(rt1), 11)

        rt2 = r.tree(v=False).split("\n")
        self.assertFalse(" | | - <®::int(22)>" in rt2)
        self.assertEqual(len(rt2), 4)

        r.î([2], lambda e: e.data(
           a="b"*20, c="d"*20, e="f"*20, g="h"*20, i="j"*20, k="l"*20))
        
        self.assertEqual(r.tree(), """
 <®::/4...>
 - <®::int(1)>
 - <®::int(2)>
 | <®::/3... {a=bbbbbbbbbbbbbbbbbbbb,c=dddddddddddddddddddd,e=ffffffffffffffffffff,g=hhhhhhhhhhhhhhhhhh
       hh,i=jjjjjjjjjjjjjjjjjjjj,k=llllllllllllllllllll}>
 | - <®::int(11)>
 | | <®::/2...>
 | | - <®::int(21)>
 | | - <®::int(22)>
 | - <®::int(13)>
 - <®::int(3)>""")

if __name__ == "__main__":
    unittest.main()