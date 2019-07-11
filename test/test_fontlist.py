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

fonts = sorted(fonts, key=str.lower)[:30]
#fonts = [f for f in fonts if "sans" in f]

with previewer() as p:
    for f in fonts:
        r = Rect((0, 0, 500, 120))
        fp = f"{font_dir}/{f}"
        ss = StyledString("Three Gems Tea", font=fp, fontSize=72, trackingLimit=0, tracking=0, variations=dict(wdth=1, wght=1, slnt=1, scale=True))
        dp = ss.asDAT().addAttrs(fill=0)
        dp.translate(20, 20)
        p.send(SVGPen.Composite([dp], r), rect=r)
        p.send(fp, rect=Rect((0, 0, 500, 30)))
    #p.send(SVGPen.Composite([dp1], r), rect=r)