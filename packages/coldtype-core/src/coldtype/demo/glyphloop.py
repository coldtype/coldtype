from coldtype import *
from coldtype.tool import parse_inputs

args = parse_inputs(__inputs__, dict(
    font=[None, str, "Must provide font regex or path"],
    showChars=[False, bool]))

fnt = Font.Find(args["font"])

os2 = fnt.font.ttFont["OS/2"]
glyphSet = fnt.font.ttFont.getGlyphSet()
glyphs = glyphSet.keys()

@animation((1920, 1080), tl=Timeline(len(glyphs), 24), bg=0)
def glyphViewer(f):
    glyphKey = glyphs[f.i]
    glyph = glyphSet[glyphKey]
    
    return (P(
        P().glyph(glyph, glyphSet).data(frame=Rect(0, 0, glyph.width, os2.sCapHeight))
            .f(1)
            .align(f.a.r, tx=0)
            .scale(0.5, tx=0)
            .scaleToRect(f.a.r.inset(100), shrink_only=True, preserveAspect=True),
        StSt("{:04d}".format(f.i), fnt, 60)
            .f(1)
            .align(f.a.r.inset(100), "SW", tx=0)
            .null()))