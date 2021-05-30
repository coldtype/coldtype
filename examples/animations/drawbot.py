from coldtype import *
from coldtype.drawbot import dbdraw, dbdraw_with_filters, db

co = Font("assets/ColdtypeObviously-VF.ttf")

@drawbot_animation(timeline=Timeline(30), bg=None)
def stub(f):
    e = f.a.progress(f.i, loops=1, easefn="eeo").e
    fs = db.FormattedString("COLDTYPE",
        font=co.path, fontSize=120, fontVariations=dict(wdth=e*1000))
    bp = db.BezierPath()
    bp.text(fs, (100, 100))
    db.fill(*hsl(0, 0.6))
    db.drawPath(bp)