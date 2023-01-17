import unittest
from pathlib import Path
from coldtype.renderable import renderable, Action
from coldtype.renderer.reader import SourceReader


test_src = """
from coldtype import *

@renderable()
def test_src_function(r):
    return (StSt("CDELOPTY",
        "assets/ColdtypeObviously-VF.ttf")
        .align(r.inset(50))
        .f(hsl(0.5, 0.7, 0.9)))

@animation()
def test_src_animation(f):
    return (StSt("CDELOPT",
        "assets/ColdtypeObviously-VF.ttf",
        wdth=f.e("linear", 1))
        .align(f.a.r))
"""


class TestSyntaxMods(unittest.TestCase):
    def setUp(self) -> None:
        self.sr = SourceReader(None, test_src)
        self.sr2 = SourceReader(runner="special")
        return super().setUp()

    def tearDown(self) -> None:
        self.sr.unlink()
        self.sr2.unlink()
        return super().tearDown()
    
    def test_empty_reader(self):
        self.assertEqual(self.sr2.filepath, None)
        self.assertEqual(self.sr2.codepath, None)
        self.sr2.reset_filepath("test/source_file.py")
        self.assertEqual(self.sr2.filepath.stem, "source_file")
        self.assertEqual(len(self.sr2.renderables()), 1)
        self.assertEqual(self.sr2.program["__RUNNER__"], "special")
        self.assertEqual(self.sr2.program["hello"], "world")
    
    def test_source_with_config(self):
        sr = SourceReader("test/source_file_with_config.py")
        sr.unlink()
        self.assertEqual(sr.filepath.stem, "source_file_with_config")
        self.assertEqual(len(sr.renderables()), 2)
        self.assertEqual(sr.config.window_pin, "SW")
    
    def test_frame_read(self):
        result = self.sr.frame_results(1)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(len(result[0][1]), 8)

    def test_syntax_mods(self):
        return
        sr = self.sr
        sr.reload(output_folder_override="test/renders")
        mod_src = sr.codepath.read_text()

        self.assertIn(".align(r.inset(50))", test_src)
        self.assertNotIn(".align(r.inset(50))", mod_src)
        self.assertIn(".noop()", mod_src)

        self.assertEqual(sr.program["__RUNNER__"], "default")

        renderables = sr.renderables()
        self.assertEqual(len(renderables), 2)
        self.assertEqual(renderables[0].codepath, sr.codepath)

        r1:renderable = renderables[0]
        r1_passes = r1.passes(None, None, [])
        r1p1_result = r1.run_normal(r1_passes[0])
        self.assertEqual(r1p1_result[3].glyphName, "L")

        r2:renderable = renderables[1]
        r2_passes = r2.passes(Action.RenderAll, None, [])
        for idx, rp in enumerate(r2_passes):
            rel = rp.output_path.relative_to(Path.cwd() / "test/renders")
            self.assertEqual(
                "test_src_animation_{:04}.png".format(idx),
                str(rel))
        
        # verify that the width of the 'C' is increasing over the first half of the animation
        r2p2_result = r2.run_normal(r2_passes[1])
        r2p3_result = r2.run_normal(r2_passes[2])
        r2p4_result = r2.run_normal(r2_passes[3])
        self.assertLess(
            r2p2_result[0].ambit().w,
            r2p3_result[0].ambit().w)
        self.assertLess(
            r2p3_result[0].ambit().w,
            r2p4_result[0].ambit().w)

        renderables = sr.renderables(viewer_solos=[1])
        self.assertEqual(len(renderables), 1)
        self.assertEqual(renderables[0].name, "test_src_animation")
    
        # indexes over len wrap-around
        renderables = sr.renderables(viewer_solos=[2])
        self.assertEqual(len(renderables), 1)
        self.assertEqual(renderables[0].name, "test_src_function")

        renderables = sr.renderables(function_filters=[r".*_function"])
        self.assertEqual(len(renderables), 1)
        self.assertEqual(renderables[0].name, "test_src_function")

        renderables = sr.renderables(function_filters=[r".*_animation"])
        self.assertEqual(len(renderables), 1)
        self.assertNotEqual(renderables[0].name, "test_src_function")

        renderables = sr.renderables(class_filters=[r".*asdf$"])
        self.assertEqual(len(renderables), 0)

        renderables = sr.renderables(class_filters=[r".*ation$"])
        self.assertEqual(len(renderables), 1)
        self.assertEqual(renderables[0].__class__.__name__, "animation")

        # when the pattern matches nothing, all renderables returned
        renderables = sr.renderables(function_filters=[r".*_should_be_nothing"])
        self.assertEqual(len(renderables), 2)
    
        #sr.reload(test_src.replace("-.align(", ".align("))
        mod_src = sr.codepath.read_text()
        self.assertNotIn(".noop()", mod_src)
        self.assertIn(".align(r.inset(50))", mod_src)

        prev_codepath = sr.codepath
        prev_filepath = sr.filepath
        test_source_file = Path("test/source_file.py")
        sr.reset_filepath("test/source_file.py")

        self.assertEqual(sr.filepath.absolute(), test_source_file.absolute())
        self.assertNotEqual(sr.codepath, prev_codepath)

        self.assertTrue(not prev_filepath.exists())
        self.assertTrue(not prev_codepath.exists())
        self.assertTrue(sr.codepath.exists())

        sr.unlink()

        self.assertTrue(not sr.codepath.exists())
        self.assertTrue(test_source_file.exists())

        sr.reset_filepath("test/source_file")
        self.assertEqual(sr.filepath.suffix, ".py")
        self.assertEqual(sr.filepath, test_source_file.absolute())

if __name__ == "__main__":
    unittest.main()