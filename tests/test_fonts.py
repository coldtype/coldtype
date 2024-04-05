from coldtype.test import *
from coldtype.text.font import FontmakeCache

@test()
def test_fontmake(r):
    out = P()

    src = "assets/ColdtypeObviously_CompressedBlackItalic.ufo"
    font = Font.Fontmake(src)
    
    out.append(StSt("COLD", font, 100))
    
    assert list(FontmakeCache.keys())[0] == Path(src)
    assert isinstance(font, Font)

    src = "assets/ColdtypeObviously.designspace"
    font = Font.Fontmake(src)

    out.append(StSt("TYPE", font, 100))

    assert Path(font.path).suffix == ".ttf"
    assert list(FontmakeCache.keys())[1] == Path(src)
    assert isinstance(font, Font)

    assert len(out) == 2
    assert len(out[0]) == 4
    assert len(out[1]) == 4
    
    assert out[0][0].data("glyphName") == "C"
    assert out[-1][-1].data("glyphName") == "E"

    return out.stack(10).align(r)