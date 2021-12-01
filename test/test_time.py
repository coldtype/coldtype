import unittest
from coldtype.time.nle.ascii import AsciiTimeline
from coldtype.renderable.animation import animation
from coldtype.renderer.reader import SourceReader
from coldtype.time.timeable import Timeable

at = AsciiTimeline(1, """
                                    |
[a          ]
        [b          ]
                [c          ]
     ]                  [d          
""")

at2 = AsciiTimeline(1, """
1
        2
                3
                        [four  ]
""")

class TestTime(unittest.TestCase):
    def test_ascii_timeline_1(self):
        self.assertEqual(at.duration, 36)
        self.assertEqual(at["a"][0].start, 0)
        self.assertEqual(at["b"][0].end, 21)
        self.assertEqual(at["c"][0].start, 16)
        self.assertEqual(at["d"][0].end, 41)
        self.assertEqual(len(at.timeables), 4)

        self.assertEqual(at.ki("a", 0).e(), 0)
        self.assertAlmostEqual(at.ki("a", 4).e(loops=0), 0.0347, 3)
        self.assertAlmostEqual(at.ki("a", 4).e(loops=1), 0.8990, 3)

        self.assertNotEqual(at.ki("b", 20).e(loops=0, to1=0), 1)
        self.assertEqual(at.ki("b", 20).e(loops=0, to1=1), 1)

        self.assertEqual(at[1].start, -1)
        self.assertEqual(at.ki(1, 30).t.start, -1)

        self.assertEqual(at.ki("b", 8).io(5), 0)
        self.assertEqual(at.ki("b", 8+5).io(5), 1)
    
    def test_ascii_timeline_2(self):
        self.assertEqual(at2.duration, 31)

        self.assertIsInstance(at2["1"][0], Timeable)
        self.assertEqual(at2[1][0].duration, 0)
        self.assertEqual(at2.ki("2", 8).adsr(), 1)
        self.assertEqual(at2.ki("2", 0).adsr(), 0)
        self.assertAlmostEqual(at2.ki("2", 8+18).adsr([5, 20]), 0.001, 3)
        self.assertAlmostEqual(at2.ki("2", 8+18).adsr([5, 20], ["eei", "qeio"]), 0.0055, 3)
        self.assertEqual(at2.ki("2", 8+3).adsr([5, 5, 20], ["eei", "qeio"], rng=(10, -10)), -10)

        at2.hold(8+18)
        self.assertAlmostEqual(at2.ki("2").adsr([5, 20], ["eei", "qeio"]), 0.0055, 3)
    
    def test_animation(self):
        src = "test/visuals/test_animation.py"
        sr = SourceReader(src).unlink()
        anim:animation = sr.renderables()[0]
        
        self.assertEqual(anim.duration, 26)
        self.assertEqual(anim.t.find_workarea(), [0, 1, 2])
        
        for i in range(0, anim.duration):
            p = anim.passes(None, None, indices=[i])[0]
            res = anim.run_normal(p)
            gn = chr(65+i)
            if gn == "I":
                gn = "I.narrow"
            self.assertEqual(res[0][0].glyphName, gn)
            if i == 13:
                self.assertAlmostEqual(res[0][0].f().h/360, 0)

if __name__ == "__main__":
    unittest.main()