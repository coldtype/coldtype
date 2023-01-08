import unittest
from coldtype.timing.nle.ascii import AsciiTimeline
from coldtype.renderable.animation import animation, Frame
from coldtype.renderer.reader import SourceReader
from coldtype.timing.timeable import Timeable
from coldtype.timing.timeline import Timeline
from coldtype.text import Font, Style, Rect

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

at3 = AsciiTimeline(1, 24, """
                                                    <
        .style1
*Oh,    hello.  •   *This   some
                        is      t  +x  +t       •
""")

at4 = AsciiTimeline(1, 30, """
                                    <
[0   ]     [0  ]     [0 ] [0   ]
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
    
    def test_ascii_timeline_3(self):
        from coldtype.timing.sequence import ClipTrack, ClipGroup, Clip, ClipType

        self.assertEqual(at3.duration, 52)
        self.assertEqual(at3.fps, 24)

        ct = at3.words
        self.assertIsInstance(ct, ClipTrack)
        self.assertIsInstance(ct.styles, Timeline)
        self.assertEqual(len(ct.styles), 1)
        self.assertEqual(ct.styles[0].name, "style1")

        cg:ClipGroup = ct.currentGroup(0)
        self.assertEqual(len(cg.clips), 3)
        self.assertEqual(cg.clips[0].type, ClipType.ClearScreen)
        self.assertEqual(cg.clips[0].text, "Oh,")
        self.assertEqual(cg.clips[1].type, ClipType.Isolated)
        self.assertEqual(cg.clips[1].text, "hello.")
        self.assertEqual(cg.clips[-1].type, ClipType.EndCap)
        self.assertEqual(cg.clips[-1].text, "")

        cg:ClipGroup = ct.currentGroup(16)
        self.assertEqual(cg.duration, 0)

        cg:ClipGroup = ct.currentGroup(19)
        self.assertEqual(cg.duration, 0)

        cg:ClipGroup = ct.currentGroup(20)
        self.assertNotEqual(cg.duration, 0)

        cg:ClipGroup = ct.currentGroup(28)
        self.assertEqual(len(cg.clips), 7)
        self.assertEqual(cg.clips[0].type, ClipType.ClearScreen)
        self.assertEqual(cg.clips[-1].type, ClipType.EndCap)
        self.assertEqual(cg.clips[-1].text, "")

        def styler(c):
            if "style1" in c.styles:
                return c.text, Style(Font.RecursiveMono(), 150)
            else:
                return c.text.upper(), Style(Font.MutatorSans(), 150)

        cgp = cg.pens(Frame(28, at3), styler, Rect(1080, 1080))
        self.assertEqual(len(cgp), 1)
        self.assertEqual(len(cgp[0]), 4)
        self.assertEqual(cgp[0].data("line_text"), "This is some txt")
        self.assertEqual(cgp[0][0][0].data("position"), 1)
        self.assertEqual(cgp[0][1][0].data("position"), 0)
        self.assertEqual(cgp[0][2][0].data("position"), -1)
        self.assertEqual(cgp[0][1][0][-2].glyphName, "S.closed")
    
    def test_ascii_timeline_ec(self):
        self.assertEqual(at4.duration, 36)

        self.assertEqual(at4.ki(0, 0).ec("l", rng=(0, 90)), 0)
        self.assertEqual(at4.ki(0, 10).ec("l", rng=(0, 90)), 90)
        self.assertEqual(at4.ki(0, 35).ec("l", rng=(0, 90)), 360)
    
    def test_animation(self):
        src = "examples/animations/alphabet.py"
        sr = SourceReader(src).unlink()
        anim:animation = sr.renderables()[0]
        
        self.assertEqual(anim.duration, 26)
        
        for i in range(0, anim.duration):
            p = anim.passes(None, None, indices=[i])[0]
            res = anim.run_normal(p)
            gn = chr(65+i)
            if gn == "I":
                gn = "I.narrow"
            self.assertEqual(res[1][0][0].glyphName, gn)
            if i == 13:
                self.assertAlmostEqual(res[1][0][0].f().h/360, 0)

if __name__ == "__main__":
    unittest.main()