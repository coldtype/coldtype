from coldtype import *
from drawBot import *
import coldtype.drawbot as ctdb


@drawbot_animation((500, 200))
def multipage_doc(f):
    c = hsl(f.a.progress(f.i).e, s=0.5, l=0.5)
    (DATPen(f.a.r)
        .f(c)
        .chain(ctdb.dbdraw))
    fontSize(50)
    fill(1)
    textBox("Page " + str(f.i), f.a.r.inset(50))


def release(passes):
    ctdb.pdfdoc(multipage_doc,
        "examples/drawbot/drawbot_multipage.pdf")
    
multipage_doc_contactsheet = multipage_doc.contactsheet(2)