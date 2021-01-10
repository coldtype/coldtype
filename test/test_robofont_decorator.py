from coldtype import *

import json

class RoboFontData():
    def __init__(self, ufo_path):
        self.ufo_path = normalize_font_path(ufo_path)
        self.path = Path("~/robofont-coldtype.json").expanduser()
        self.data = {}
        self.ufo = None
    
    def read(self):
        #try:
        self.ufo = raw_ufo(self.ufo_path)
        #except:
        #    pass
        try:
            self.data = json.loads(self.path.read_text())
        except json.JSONDecodeError:
            pass
        
        layers = {}
        for lk, lv in self.data["layers"].items():
            layers[lk] = DATPen().vl(lv["value"]).addFrame(Rect(lv["width"], 1000))
        
        return self.data["name"], layers

#class robofont_viewer(renderable):
#    def __init__(self, **kwargs):
#        self.datafile_path = Path("~/robofont-coldtype.json").expanduser()

rfd = RoboFontData("~/Type/ex1/greektown/greektown.ufo")

def fontview(p:DATPen, r:Rect):
    f = p.getFrame()
    p.f(0).translate(100, 250)
    return DATPenSet([
        DATPen().gridlines(r, 50, absolute=True),
        DATPen().line([[100, 0], [100, r.h]]).f(None).s(0),
        DATPen().line([[100+f.w, 0], [100+f.w, r.h]]).f(None).s(0),
        DATPen().line([[0, 1000], [r.w, 1000]]).f(None).s(0),
        DATPen().line([[0, 250], [r.w, 250]]).f(None).s(0),
        p.copy().removeOverlap().f(None).s(hsl(0.9, s=1, a=0.5)).sw(5),
        #p.copy().removeOverlap().f(None).s(hsl(0)).sw(15).color_phototype(r)
        ])

@renderable((2000, 1200), watch_soft=[rfd.path])
def stub(r):
    gn, gls = rfd.read()
    return [
        #DATPen().glyph(rfd.ufo["P"]).translate(100, 250).f(hsl(0.7, 1, 0.8, 0.5)),
        gls["foreground"].f(0).replace(fontview, r)
    ]