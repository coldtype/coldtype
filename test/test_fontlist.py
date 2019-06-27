from test_preamble import *

r = Rect((0, 0, 500, 500))
dp1 = DATPen(fill=Color.from_html("deeppink"))
dp1.oval(r.inset(20, 20))

with previewer() as p:
    p.send(SVGPen.Composite([dp1], r), rect=r)