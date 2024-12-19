from coldtype.test import *
from coldtype.text.font import FontmakeCache

@test()
def test_instances(r):
    font = Font.MutatorSans()
    instances = font.instances(scaled=True)
    
    assert len(instances) == 6

    out = StyledString("HIHI", Style(font, 100, instance="BoldCondensed"))

    assert out.variations["wdth"] == instances["BoldCondensed"]["wdth"]*1000
    assert out.variations["wght"] == instances["BoldCondensed"]["wght"]*1000

    return out.pens().align(r).f(0)

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