from coldtype import *
from coldtype.drawbot import *

font = Font.RecursiveMono()

@drawbot_animation("letter")
def multipage_doc(f):
    c = hsl(f.e("l", 0))
    
    P(f.a.r.inset(10)).f(c).outline(10).ch(dbdraw)
    
    fontName = db.installFont(str(font.path))
    fs = db.FormattedString(
        f"This is page {f.i}"
        , font=fontName
        , fontSize=50
        , fill=c.rgba())
    
    db.textBox(fs, f.a.r.inset(50))
    
    bp = db.BezierPath()
    bp.textBox(fs, f.a.r.inset(50, 100))
    db.fill(*c)
    db.drawPath(bp)

    (StSt(f"This is page {f.i}", font, 50)
        .f(c)
        .align(f.a.r.inset(50, 160), "NW", tx=0)
        .ch(dbdraw))


# hit the 'R' key in the viewer to trigger this

def release(_):
    pdfdoc(multipage_doc,
        __sibling__("multipage.pdf"))