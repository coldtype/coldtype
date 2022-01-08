import datetime
from subprocess import run

from coldtype import *
from coldtype.pens.dattext import DATText

cap_height = 750
descender = -250
font_name = "Generative"
style_name = "Regular"

# decorator class to wrap glyph-building functions

class glyphfn():
    def __init__(self, width=1000, lsb=0, rsb=0):
        """lsb = left-side-bearing / rsb = right-side-bearing"""
        self.lsb = lsb
        self.rsb = rsb
        self.frame = Rect(width, cap_height)
        self.bbox = Rect(lsb + width + rsb, cap_height)
    
    def __call__(self, func):
        self.func = func
        self.glyph_name = func.__name__
        self.unicode = glyph_to_uni(self.glyph_name)
        return self

# !!! the important part:
# individual functions to draw glyphs
# the function names should be canonical
# "glyphNames" as in assets/glyphNamesToUnicode.txt

@glyphfn(300)
def space(r):
    return DP() # i.e. nothing (since it's a blank space)

@glyphfn(500, 10, 10)
def A(r):
    return (P()
        .rect(r)
        .difference(DP(r.take(100, "mdy")
            .take(20, "mdx")
            .offset(0, 100)))
        .difference(DP(r.take(200, "mny")
            .take(20, "mdx"))))

@glyphfn(500, 10, 10)
def B(r):
    t, b = r.inset(0, 100).subdivide(2, "mxy")
    return (P()
        .rect(r)
        .difference(DP(t.take(100, "mdy")
            .take(20, "mdx")))
        .difference(DP(b.take(100, "mdy")
            .take(20, "mdx")))
        .difference(DP(r.take(100, "mdy")
            .take(100, "mxx"))
            .rotate(45)
            .translate(50, 0)))

@glyphfn(500, 10, 10)
def C(r):
    return (P()
        .rect(r)
        .difference(DP(r.take(20, "mdx")
            .inset(0, 250)))
        .difference(DP(r.take(0.5, "mxx")
            .take(20, "mdy"))))

# !!! end of glyph drawing functions

def find_glyph_fns():
    found = []
    itms = globals().items()
    for k, v in itms:
        if isinstance(v, glyphfn):
            found.append(v)
    return found

glyph_fns = find_glyph_fns()

# our useable output is a UFO file,
# which we should make sure exists
ufo_path:Path = __sibling__("generative_font.ufo")
if not ufo_path.exists():
    ufo = DefconFont()
    ufo.save(ufo_path)

def show_grid(render, result):
    if False: # flip to true if you don't want to see the grid
        return result

    gfn = result[0].data.get("gfn")
    if not gfn:
        print("! No glyph found")
    else:
        bbox = gfn.bbox.offset(0, 250)
        return P([
            P(result).translate(0, 250),
            P().gridlines(render.rect).s(hsl(0.6, a=0.3)).sw(1).f(None),
            (P()
                .line(bbox.es.extr(-100))
                .line(bbox.en.extr(-100))
                .line(bbox.ee.extr(-100))
                .f(None)
                .s(hsl(0.9, 1, a=0.5))
                .sw(4)),
            (DATText(gfn.glyph_name,
                Style("Times", 48, load_font=0),
                render.rect.inset(50)))
        ])

preview_frame = Rect(1000, (-descender*2)+cap_height)

@animation(preview_frame, timeline=Timeline(len(glyph_fns)), postfn=show_grid)
def glyph_viewer(f):
    glyph_fn = glyph_fns[f.i]
    
    ufo = DefconFont(ufo_path)
    ufo.info.familyName = font_name
    ufo.info.styleName = style_name
    ufo.info.capHeight = cap_height
    ufo.info.ascender = cap_height
    ufo.info.descender = descender
    ufo.info.unitsPerEm = 1000

    print(f"> drawing :{glyph_fn.glyph_name}:")
    glyph_pen = glyph_fn.func(glyph_fn.frame).f(0)

    # shift over by the left-side-bearing
    glyph_pen.translate(glyph_fn.lsb, 0)
    glyph = glyph_pen.toGlyph(
        name=glyph_fn.glyph_name,
        width=glyph_fn.frame.w + glyph_fn.lsb + glyph_fn.rsb,
        allow_blank = True)
    glyph.unicode = glyph_to_uni(glyph_fn.glyph_name)
    ufo.insertGlyph(glyph)
    ufo.save()
    return glyph_pen.addData("gfn", glyph_fn)


@renderable((1080, 300))
def font_previewer(r):
    """
    This function loads the ufo that’s been created by the code
    above and displays it "as a font" (i.e. it compiles the ufo
    to a font and then uses the actual font to do standard font-
    display logic)
    """
    ufo = Font(ufo_path)
    return (StyledString("ABC CBA",
        Style(ufo, 150))
        .pens()
        .align(r)
        .f(0))

# to run this code, go to the viewer
# app while it’s running, then hit cmd+l
# N.B. you'll need to have `fontmake`
# available in your virtualenv, which
# should be as easy as `pip install fontmake`
# with the virtualenv activated

def release(_):
    ufo = DefconFont(ufo_path)
    date = datetime.datetime.now().strftime("%y%m%d%H%M")
    font_name = "_".join([
        ufo.info.familyName.replace(" ", ""),
        ufo.info.styleName.replace(" ", ""),
        date
    ])
    fontmade_path = ufo_path.parent / f"fontmakes/{font_name}.otf"
    fontmade_path.parent.mkdir(exist_ok=True)
    run([
        "fontmake",
        "-u", str(ufo_path),
        "-o", "otf",
        "--output-path=" + str(fontmade_path)])