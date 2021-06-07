import unittest
from coldtype.time.nle.ascii import AsciiTimeline

at = AsciiTimeline(2, """
                                    |
[a          ]
        [b          ]
                [c          ]
                        [d          ]
""")

class TestTime(unittest.TestCase):
    def test_ascii_timeline(self):
        self.assertEqual(at[0].start, 0)
        self.assertEqual(at[1].end, 40)
        self.assertEqual(len(at.clips), 4)

if __name__ == "__main__":
    unittest.main()