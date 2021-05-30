import unittest
from coldtype.grid import Grid
from coldtype.geometry import *
from coldtype.sh import sh, SHContext, SHLookup

def bounds(self):
    return "BOUNDS"

SHContext.bounds = bounds

class TestSh(unittest.TestCase):
    
    def test_sh_context(self):
        ctx = SHContext()
        ctx.locals["cool"] = "io"
        ctx.subs["□"] = lambda c: "ctx.constants.bx" if hasattr(c, "guides") and hasattr(c.guides, "bx") else "ctx.bounds()"
        ctx.subs["■"] = "_dps.bounds()"

        ctx.context_record("$", "constants", None,
            hello="'world'",
            yoyo=lambda _: "ma",
            aƒbƒc="cool $hello □")
        
        self.assertEqual(len(ctx.constants), 5)
        self.assertEqual(ctx.constants["yoyo"], "ma")
        self.assertEqual(ctx.constants["b"], "world")
        
        res = ctx.sh("cool $hello □")
        self.assertEqual(res, ["io", "world", "BOUNDS"])
    
    def test_sh_grid_arg(self):
        g = Grid(Rect(100, 100), "10 a 10", "a", "x y z")
        self.assertEqual(list(g.keyed.keys()), ["x", "y", "z"])
        
        ctx = SHContext()
        ctx.context_record("&", "guides", None, g)
        self.assertEqual(ctx.guides.x.w, 10)
        self.assertEqual(g.keyed["x"].h, 100)
        self.assertEqual(ctx.sh("&y")[0].w, 80)
        self.assertEqual(ctx.sh("&y•")[0], Point(50, 50))
        self.assertEqual(ctx.sh("&z⊢")[0], Line(Point(90, 0), Point(90, 100)))
    
    def test_sh_string_literal(self):
        ctx = SHContext()
        ctx.context_record("$", "defs", None,
            hello="'world'")

if __name__ == "__main__":
    unittest.main()