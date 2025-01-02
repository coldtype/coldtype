from coldtype import *
from coldtype.raster import *
#from coldtype.img.skiasvg import SkiaSVG

from bs4 import BeautifulSoup

fnt = Font.Find("hamilton sans svg")
fnt = Font.Find("california oranges svg")
ttfont = fnt.font.ttFont

glyphs = {}
for doc, start, end in ttfont["SVG "].docList:
    #dom = skia.SVGDOM.MakeFromStream(skia.MemoryStream(doc.encode('utf-8')))
    glyphs[start] = dict(doc=doc)
    if end != start:
        glyphs[end] = dict(doc=doc)

def get_img(doc):
    Path("glyph.svg").write_text(doc)

    soup = BeautifulSoup(doc, "html.parser")
    g = soup.find("g")
    transform = g["transform"]
    img = g.find("image")

    data = img["xlink:href"]

    x, y = float(img.get("x", 0)), float(img.get("y", 0))
    w, h = float(img.get("width", 0)), float(img.get("height", 0))

    print(x, y, w, h)

    img = SkiaImage.FromBase64(data)
    img.css_translate(x, h+y)
    return img, transform.split(" ")

@renderable((1080, 1080), bg=1)
def scratch(r):
    def add_image(p):
        gid = ttfont.getGlyphID(p.data("glyphName"))
        data = glyphs[gid]
        img, transform = get_img(data["doc"])

        print("AMBIT", p.ambit(tx=0, ty=0))
        
        for t in transform[:1]:
            try:
                pass
                print(t)
                eval(f"img.css_{t}")
            except Exception as e:
                print(e)

        return p.up().insert(0, P(p.ambit()).fssw(-1, 0, 1)).append(img.align(p.ambit()))

    return (StSt("XYZ", fnt, 750)
        .align(r)
        .mapv(add_image)
        #.t(100, 100)
        )
