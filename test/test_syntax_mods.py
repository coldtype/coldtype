import unittest, tempfile
from pathlib import Path
from coldtype.renderer.reader import find_renderables, read_source_to_tempfile, run_source


test_src = """
from coldtype import *

@renderable()
def test_src_function(r):
    return (StSt("CDELOPTY", "assets/ColdtypeObviously-VF.ttf")
        -.align(r)
        .f(hsl(0.5, 0.7, 0.9)))

@animation()
def test_src_animation(f):
    return (StSt("CDELOPTY", "assets/ColdtypeObviously-VF.ttf",
        wdth=f.e(1))
        .align(f.a.r))
"""


class TestSyntaxMods(unittest.TestCase):
    def test_syntax_mods(self):
        with tempfile.NamedTemporaryFile("w", prefix="coldtype_test", suffix=".py", delete=False) as tf:
            tf.write(test_src)
        
        filepath = Path(tf.name)
        codepath = read_source_to_tempfile(filepath)
        mod_src = codepath.read_text()

        self.assertIn(".align(r)", test_src)
        self.assertNotIn(".align(r)", mod_src)
        self.assertIn(".noop()", mod_src)

        program = run_source(filepath, codepath)

        renderables = find_renderables(filepath, program)
        self.assertEqual(len(renderables), 2)

        renderables = find_renderables(filepath, program,
            viewer_solos=[1])
        self.assertEqual(len(renderables), 1)
        self.assertEqual(renderables[0].name, "test_src_animation")
    
        # indexes over len wrap-around
        renderables = find_renderables(filepath, program,
            viewer_solos=[2])
        self.assertEqual(len(renderables), 1)
        self.assertEqual(renderables[0].name, "test_src_function")

        renderables = find_renderables(filepath, program,
            function_filters=[r".*_function"])
        self.assertEqual(len(renderables), 1)
        self.assertEqual(renderables[0].name, "test_src_function")

        renderables = find_renderables(filepath, program,
            function_filters=[r".*_animation"])
        self.assertEqual(len(renderables), 1)
        self.assertNotEqual(renderables[0].name, "test_src_function")

        # when the pattern matches nothing, all renderables returned
        renderables = find_renderables(filepath, program,
            function_filters=[r".*_should_be_nothing"])
        self.assertEqual(len(renderables), 2)

        Path(tf.name).unlink()
        codepath.unlink()

if __name__ == "__main__":
    unittest.main()