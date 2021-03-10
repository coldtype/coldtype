from coldtype import *
from drafting.pens.axidrawpen import AxiDrawPen

"""
https://axidraw.com/doc/py_api/#installation
--> pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip
"""

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
mis = Font.Cacheable("~/Type/fonts/fonts/_script/MistralD.otf")

@renderable(Rect(1100, 850))
def test_draw(r, layer=None):
    border = DATPen().rect(r.inset(50)).f(None).s(0).sw(2)

    letters = (StyledString("COLD",
        Style(co, 500, wdth=0.15, ro=1))
        .pen()
        .align(r)
        .flatten(5))

    hatches = DATPen()
    for idx, x in enumerate(r.inset(20).subdivide(200, "mxy")):
        if idx % 2 == 0:
            hatches.record(DATPen().rect(x))
    hatches.intersection(letters.copy())

    typel = (StyledString("Type",
        Style(mis, 500))
        .pen()
        .align(r) # TODO THIS IS BROKEN
        .flatten(5)
        .removeOverlap())
    
    typef = DATPen()
    for idx, x in enumerate(r.inset(20).subdivide(200, "mnx")):
        if idx % 2 == 0:
            typef.record(DATPen().rect(x))
    typef.rotate(45)
    typef.intersection(typel.copy())

    if layer == "border":
        return border
    if layer == "stroke":
        return letters
    if layer == "fill":
        return hatches
    if layer == "tstroke":
        return typel
    if layer == "tfill":
        return typef
    return [
        border,
        hatches.f(hsl(0.5)),
        letters.f(None).s(0).sw(5),
        typef.f(hsl(0.3)),
        typel.f(None).s(0).sw(5),
    ]

def release(_):
    pen = test_draw.func(test_draw.rect, layer="border") # TODO could encapsulate?
    ap = AxiDrawPen(pen, test_draw.rect)
    ap.draw()