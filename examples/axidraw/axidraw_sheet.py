from coldtype import *
from coldtype.axidraw import *

# interactive stopping possible?

fnt = Font.Find("CheeeVariable.ttf")
#from pprint import pprint
#pprint(fnt.variations())

@animation((200, 200), tl=(5**2, 24))
def sheet_animation(f):
    r = f.a.r.inset(40)
    return (
        StSt("D", fnt, 100, grvt=f.e("cei", 1), yest=f.e("ceo", 1))
        .align(f.a.r, ty=1)
        .removeOverlap())

@axidrawing()
def sheet(r):
    sq = math.ceil(math.sqrt(sheet_animation.timeline.duration))
    
    s = Scaffold(r.inset(150)).grid(sq, sq)
    
    cells = (s.borders().tag("cells"))
    
    letters = (P().enumerate(s, lambda x: sheet_animation
            .frame_result(x.i) # should this add a frame frame?
            .align(x.el.rect, ty=1)
            .flatten(5)
            .scale(1.00))
        .tag("letters"))

    registration = (P().enumerate(s, lambda x: P()
            .line([(_r:=x.el.rect.inset(10).take(10, "NE")).pse, _r.pnw])
            #.line([_r.pnw, _r.pse])
            #.line([(_r:=x.el.rect.inset(10).take(10, "SW")).psw, _r.pne])
            #.line([_r.pnw, _r.pse])
            )
        .tag("registration"))
    
    return P(
        P(s.r).tag("border"),
        cells,
        letters.pen(),
        registration,
        #message.pen(),
        )

numpad = {
    1: sheet.draw("border"),
    2: sheet.draw("cells"),
    3: sheet.draw("letters"),
    4: sheet.draw("registration"),
}