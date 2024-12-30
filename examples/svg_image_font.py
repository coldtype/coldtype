from coldtype import *
from coldtype.raster import *

import xml.etree.ElementTree as ET

import skia

fnt = Font.Find("california oranges")
ttfont = fnt.font.ttFont

glyphs = {}
for doc, start, end in ttfont["SVG "].docList:
    #dom = skia.SVGDOM.MakeFromStream(skia.MemoryStream(doc.encode('utf-8')))
    #print(dom)

    parsed = ET.fromstring(doc)
    g = parsed.find(".//{http://www.w3.org/2000/svg}g")
    
    transform = g.attrib.get("transform", "")
    img = g.find(".//{http://www.w3.org/2000/svg}image")
    data = img.attrib.get("{http://www.w3.org/1999/xlink}href", "")#.split(",")[1]
    img = SkiaImage.FromBase64(data)

    transform = transform.split(" ")

    glyphs[start] = dict(img=img, transform=transform)
    if end != start:
        glyphs[end] = dict(img=img, transform=transform)

@renderable((1080, 540), bg=1)
def scratch(r):
    def add_image(p):
        gid = ttfont.getGlyphID(p.data("glyphName"))
        data = glyphs[gid]
        
        img = data["img"].copy()#.align(p.ambit())
        
        #for t in data["transform"]:
        #    img = eval(f"img.{t}")

        return (p.up().append(img.align(p.ambit())))

    return (StSt("Hello", fnt, 600)
        .align(r)
        .mapv(add_image))
