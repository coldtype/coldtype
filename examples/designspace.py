from coldtype import *

ds = Path(__FILE__).parent.parent / "assets/ColdtypeObviously.designspace"
varfont = Font.Cacheable(ds)

ufo = Path(__FILE__).parent.parent / "assets/ColdtypeObviously_CompressedBlackItalic.ufo"

@renderable((1080, 540))
def variable(r):
    return (Glyphwise("COLD", lambda x: Style(varfont, 500, wdth=x.e))
        .align(r))

@renderable((1080, 540))
def static(r):
    return (StSt("COLD", ufo, 500).align(r))