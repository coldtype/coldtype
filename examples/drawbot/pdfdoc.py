from coldtype import *
from coldtype.drawbot import db, dbdraw, pdfdoc


@drawbot_animation("letter")
def multipage_doc(f):
    c = hsl(f.a.progress(f.i).e, s=0.5, l=0.5)
    (DATPen(f.a.r)
        .f(c)
        .ch(dbdraw))
    
    db.fontSize(50)
    db.fill(1)
    db.textBox("This is page " + str(f.i), f.a.r.inset(50))


# hit the 'R' key in the viewer to trigger this
def release(_):
    pdfdoc(multipage_doc,
        "examples/drawbot/drawbot_multipage.pdf")