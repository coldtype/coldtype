from coldtype import *
from coldtype.drawbot import *

co = Font.ColdObvi()

@drawbot_animation((1080, 540)
, timeline=Timeline(30)
, bg=hsl(0.8, 0.6, 0.85)
, render_bg=1
)
def bounce(f):
    # Using mostly DrawBot API

    fontSize = 190

    fs = db.FormattedString("COLDTYPE",
        font=co.path,
        fontSize=fontSize,
        fontVariations=dict(
            wdth=f.e("eeio", rng=(0, 1000))))
    
    bp = db.BezierPath()
    bp.text(fs, (50, 50))
    db.fill(*hsl(0.4))
    db.drawPath(bp)

    # Using mostly Coldtype API

    (StSt("COLDTYPE", co, fontSize
        , wdth=f.e("eeio"))
        .t(50, 210)
        .f(hsl(0.4))
        .ch(dbdraw))