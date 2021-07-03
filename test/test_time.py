import unittest
from coldtype.time.nle.ascii import AsciiTimeline
from coldtype.renderable.animation import animation
from coldtype.renderer.reader import SourceReader

at = AsciiTimeline(1, """
                                    |
[a          ]
        [b          ]
                [c          ]
     ]                  [d          
""")

class TestTime(unittest.TestCase):
    def test_ascii_timeline(self):
        self.assertEqual(at.duration, 36)
        self.assertEqual(at[0].start, 0)
        self.assertEqual(at[1].end, 21)
        self.assertEqual(at[2].start, 16)
        self.assertEqual(at[-1].end, 41)
        self.assertEqual(len(at.clips), 4)
    
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