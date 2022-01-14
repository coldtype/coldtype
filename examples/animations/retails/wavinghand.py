from coldtype import *

@animation()
def peace(f):
    txtfont = "Degular-Black"
    return (StSt("Peace ✌ !", txtfont, 100, space=230)
        .replaceGlyph(".notdef", StSt("✌", "Gooper", 100))
        .align(f.a.r)
        .findGlyph("uni270C", lambda p: p
            .translate(3, -5)
            .rotate(f.e("seio", r=(-20, 20))))
        .f(0))