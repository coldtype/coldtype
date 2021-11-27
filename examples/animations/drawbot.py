from coldtype import *
from coldtype.drawbot import *

co = Font("assets/ColdtypeObviously-VF.ttf")

@drawbot_animation((1080, 300), timeline=Timeline(30), bg=1)
def bounce(f):

    # Using mostly DrawBot API

    fs = db.FormattedString("COLDTYPE",
        font=co.path,
        fontSize=120,
        fontVariations=dict(
            wdth=f.e("eeio", 1, rng=(0, 1000))))
    
    bp = db.BezierPath()
    bp.text(fs, (50, 50))
    db.fill(*hsl(0.4))
    db.drawPath(bp)

    # Using mostly Coldtype API

    (StSt("COLDTYPE", co, 120, wdth=f.e("eeio", 1))
        .t(50, 150)
        .f(hsl(0.4))
        | dbdraw)