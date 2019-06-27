from test_preamble import *
from pprint import pprint

r = Rect((0, 0, 500, 500))
dp1 = DATPen(fill=Color.from_html("deeppink"))
dp1.oval(r.inset(20, 20))

font_dir = os.path.expanduser("~/Type/fonts/fonts")
fonts = []
for f in os.listdir(font_dir):
    if f.endswith("ttf") or f.endswith("otf"):
        fonts.append(f)

fonts = sorted(fonts, key=str.lower)
fonts = [f for f in fonts if f.startswith("LoRes")]

with previewer() as p:
    for f in fonts:
        r = Rect((0, 0, 400, 120))
        fp = f"{font_dir}/{f}"
        ss = StyledString("Hello", font=fp, fontSize=72, rect=r)
        p.send(SVGPen.Composite([ss.asDAT()], r), rect=r)
        p.send(fp, rect=Rect((0, 0, 500, 30)))
    #p.send(SVGPen.Composite([dp1], r), rect=r)