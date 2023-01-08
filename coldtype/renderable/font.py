import datetime

from subprocess import run
from defcon import Font as DFont
from coldtype.geometry.rect import Rect
from coldtype.helpers import glyph_to_uni
from coldtype.timing.timeline import Timeline
from coldtype.renderable import renderable, animation
from coldtype.text.composer import Style, Font, StSt
from coldtype.runon.path import P
from coldtype.color import hsl
from pathlib import Path

from typing import Tuple


class glyphfn():
    def __init__(self, width=1000, lsb=0, rsb=0):
        """lsb = left-side-bearing / rsb = right-side-bearing"""
        self.width = width
        self.lsb = lsb
        self.rsb = rsb
        self.frame = None
        self.bbox = None
    
    def add_font(self, font):
        self.frame = Rect(self.width, font.ufo.info.capHeight)
        self.bbox = Rect(self.lsb + self.width + self.rsb, font.ufo.info.capHeight)
        return self
    
    def __call__(self, func):
        self.func = func
        self.glyph_name = func.__name__
        self.unicode = glyph_to_uni(self.glyph_name)
        return self


class generativefont(animation):
    def __init__(self,
        lookup,
        ufo_path:Path,
        font_name="Test",
        style_name="Regular",
        cap_height=750,
        ascender=750,
        descender=-250,
        units_per_em=1000,
        preview_size=(1000, None),
        filter=None):

        pw, ph = preview_size
        self.preview_frame = Rect(pw, ph if ph else (-descender*2) + cap_height)

        if not ufo_path.exists():
            ufo = DFont()
            ufo.save(ufo_path)
        else:
            ufo = DFont(str(ufo_path))
        
        ufo.info.familyName = font_name
        ufo.info.styleName = style_name
        ufo.info.capHeight = cap_height
        ufo.info.ascender = ascender
        ufo.info.descender = descender
        ufo.info.unitsPerEm = units_per_em
        
        self.ufo = ufo
        self.filter = filter

        super().__init__(
            self.preview_frame, timeline=self.timeline(lookup),
            postfn=generativefont.ShowGrid)
    
    def _find_glyph_fns(self, lookup):
        """
        `lookup` should probably be `globals()`
        """
        self.glyph_fns = []
        itms = lookup.items()
        for k, v in itms:
            if isinstance(v, glyphfn):
                self.glyph_fns.append(v)
    
    def timeline(self, lookup):
        self._find_glyph_fns(lookup)
        return Timeline(len(self.glyph_fns))
    
    def frame_to_fn(self, fi) -> Tuple[str, dict]:
        return [
            f"def {self.glyph_fns[fi].glyph_name}(",
            dict(decorator="@glyphfn")]
    
    def ShowGrid(render, result):
        if False: # flip to true if you don't want to see the grid
            return result

        gfn = result[0].data.get("gfn")
        if not gfn:
            print("! No glyph found")
            return result
        
        try:
            guides = result[0].all_guides()
        except:
            guides = P()
        
        bbox = gfn.bbox.offset(0, 250)
        return P([
            P(result).translate(0, 250),
            #P().gridlines(render.rect).s(hsl(0.6, a=0.3)).sw(1).f(None),
            (P()
                .line(bbox.es.extr(-100))
                .line(bbox.en.extr(-100))
                .line(bbox.ee.extr(-100))
                .f(None).s(hsl(0.9, 1, a=0.5)).sw(4)),
            guides.translate(gfn.lsb, 250),
            (P().text(gfn.glyph_name, Style("Times", 48, load_font=0),
                render.rect.inset(50)))])
    
    def glyphViewer(self, f):
        glyph_fn = self.glyph_fns[f.i]
        glyph_fn.add_font(self)

        print(f"> drawing :{glyph_fn.glyph_name}:")
        glyph_pen = (glyph_fn
            .func(glyph_fn.frame)
            .fssw(-1, 0, 2))
        
        if self.filter:
            glyph_pen = self.filter(glyph_pen)

        # shift over by the left-side-bearing
        glyph_pen.translate(glyph_fn.lsb, 0)
        glyph = glyph_pen.toGlyph(
            name=glyph_fn.glyph_name,
            width=glyph_fn.frame.w + glyph_fn.lsb + glyph_fn.rsb,
            allow_blank = True)
        glyph.unicode = glyph_to_uni(glyph_fn.glyph_name)
        self.ufo.insertGlyph(glyph)
        self.ufo.save()
        return P([
            glyph_pen.data(gfn=glyph_fn)
        ])
    
    def spacecenter(self, r, text, fontSize=150):
        """
        This function loads the ufo that’s been created by the code above and displays it "as a font" (i.e. it compiles the ufo to a font and then uses the actual font to do standard font-display logic)
        """
        ufo = Font(self.ufo.path)
        return (StSt(text, ufo, fontSize)
            .align(r)
            .f(0))

    def fontmake(self):
        ufo = DFont(self.ufo.path)
        date = datetime.datetime.now().strftime("%y%m%d%H%M")
        font_name = "_".join([
            ufo.info.familyName.replace(" ", ""),
            ufo.info.styleName.replace(" ", ""),
            date
        ])
        fontmade_path = self.ufo.path.parent / f"fontmakes/{font_name}.otf"
        fontmade_path.parent.mkdir(exist_ok=True)
        run([
            "fontmake",
            "-u", str(self.ufo.path),
            "-o", "otf",
            "--output-path=" + str(fontmade_path)])