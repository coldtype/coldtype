from coldtype import *
from coldtype.drawbot import *

co = Font("assets/ColdtypeObviously-VF.ttf")

@drawbot_animation((1080, 300), timeline=Timeline(30), bg=1)
def bounce(f):
    fs = db.FormattedString("COLDTYPE",
        font=co.path,
        fontSize=120,
        fontVariations=dict(
            wdth=f.e("eeo", 1, rng=(0, 1000))))
    
    bp = db.BezierPath()
    bp.text(fs, (100, 100))
    db.fill(*hsl(0.4))
    db.drawPath(bp)