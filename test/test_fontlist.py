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

#fonts = sorted(fonts, key=str.lower)[:10]
fonts = [f for f in fonts if "Biblio" in f]

with previewer() as p:
    for f in fonts:
        r = Rect((0, 0, 600, 120))
        fp = f"{font_dir}/{f}"
        dp = Slug("Three Gems Tea", Style(fp, 72, fill=0)).pen().translate(20, 20)
        p.send(SVGPen.Composite([dp], r), rect=r)
        p.send(fp, rect=Rect((0, 0, 500, 30)))
    #p.send(SVGPen.Composite([dp1], r), rect=r)