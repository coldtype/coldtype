from coldtype import *
from drawBot import *
import coldtype.drawbot as ctdb


@drawbot_animation("letter")
def multipage_doc(f):
    c = hsl(f.a.progress(f.i).e, s=0.5, l=0.5)
    (DATPen(f.a.r)
        .f(c)
        .chain(ctdb.dbdraw))
    
    fontSize(50)
    fill(1)
    textBox("This is page " + str(f.i), f.a.r.inset(50))


# hit the 'R' key in the viewer to trigger this
def release(_):
    ctdb.pdfdoc(multipage_doc,
        "examples/drawbot/drawbot_multipage.pdf")