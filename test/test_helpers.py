import unicodedata, unittest
from pathlib import Path
from coldtype.helpers import glyph_to_uni, uni_to_glyph


class TestHelpers(unittest.TestCase):
    def test_glyph_to_uni(self):
        self.assertEqual(glyph_to_uni("A"), 65)
        self.assertEqual(uni_to_glyph(66), "B")
        self.assertEqual(glyph_to_uni("noondotbelow"), ord("ڹ"))


if __name__ == "__main__":
    unittest.main()