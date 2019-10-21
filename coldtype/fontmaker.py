if __name__ == "__main__":
    import os
    import sys
    dirname = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(f"{dirname}/..")

from pathlib import Path
from coldtype.geometry import Rect
from coldtype.pens.datpen import DATPen
from defcon import Font, Glyph

def pen_to_glyph(name, r, dp):
    glyph = Glyph()
    glyph.name = name
    glyph.width = r.w
    dp.replay(glyph.getPen())
    return glyph

if __name__ == "__main__":
    from coldtype.viewer import viewer
    from coldtype.pens.svgpen import SVGPen

    with viewer() as v:
        r = Rect(0, 0, 750, 750)
        dp = DATPen(fill="random").oval(r.inset(25))

        font = Font()
        font.insertGlyph(pen_to_glyph("circle", r, dp))
        font.save(str(Path("~/Desktop/testfont.ufo").expanduser()))

        dp2 = DATPen()
        dp2.glyph(font["circle"])
        v.send(SVGPen.Composite(dp2, r), r, bg=1)