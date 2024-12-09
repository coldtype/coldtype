# Installing as little of Coldtype as possible, to leave breathing room for the 'from drawBot import *'

from coldtype import Font
from coldtype.drawbot import drawbot_animation
from drawBot import *

mutator = Font.MutatorSans()

@drawbot_animation(timeline=60, bg=1)
def db_varfont(f):
    fontName = installFont(str(mutator.path))
    fs = FormattedString()
    fs.fontSize(f.e("ceio", 1, rng=(150, 250)))
    fs.font(fontName)
    fs.fontVariations(
        wdth=f.e("seio", 1, rng=(0, 1000)))
    fs.append("DRAWBOT AND COLDTYPE")
    bp = BezierPath()
    bp.textBox(fs, f.a.r.inset(50, 50).expand(100, "mny"))
    drawPath(bp)