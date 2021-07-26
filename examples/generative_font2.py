from subprocess import run

from coldtype import *
from coldtype.pens.dattext import DATText
from coldtype.renderable.font import generativefont, glyphfn

# individual functions to draw glyphs
# the function names should be canonical
# "glyphNames" as in assets/glyphNamesToUnicode.txt

@glyphfn(300)
def space(r):
    return DP() # i.e. nothing (since it's a blank space)

@glyphfn(500, 10, 10)
def A(r):
    return (DATPen()
        .rect(r)
        .difference(DP(r.take(100, "mdy")
            .take(20, "mdx")
            .offset(0, 100)))
        .difference(DP(r.take(200, "mny")
            .take(20, "mdx"))))

@glyphfn(500, 10, 10)
def B(r):
    t, b = r.inset(0, 100).subdivide(2, "mxy")
    return (DATPen()
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
    return (DATPen()
        .rect(r)
        .difference(DP(r.take(20, "mdx")
            .inset(0, 250)))
        .difference(DP(r.take(0.5, "mxx")
            .take(20, "mdy"))))

@generativefont(globals(),
    __sibling__("generative_font.ufo"),
    "Generative",
    "Regular")
def gufo(f):
    return gufo.glyph_viewer(f)

@renderable((1080, 300))
def spacecenter(r):
    return gufo.spacecenter(r, "ABC CBA")

#viewer = gufo.viewer(globals())
#spacecenter = gufo.spacecenter("ABC CBA")

# to run this code, go to the viewer
# app while it’s running, then hit R
# N.B. you'll need to have `fontmake`
# available in your virtualenv, which
# should be as easy as `pip install fontmake`
# with the virtualenv activated

def release(_):
    gufo.fontmake()