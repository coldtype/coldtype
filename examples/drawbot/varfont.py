from coldtype import *
from coldtype.drawbot import *

@drawbot_animation(timeline=60)
def db_varfont(f):
    fs = db.FormattedString()
    fs.fontSize(f.e("ceio", 1, rng=(150, 300)))
    fs.font("Obviously Variable")
    fs.fontVariations(wdth=f.e("seio", 1, rng=(100, 800)))
    fs.append("DRAWBOT & COLDTYPE")
    bp = db.BezierPath()
    bp.textBox(fs, f.a.r.inset(50, 20).expand(100, "mny"))
    db.drawPath(bp)