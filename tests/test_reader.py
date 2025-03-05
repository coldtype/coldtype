from coldtype.test import *
from coldtype.osutil import on_mac, on_windows

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
mutator = Font.Cacheable("assets/MutatorSans.ttf")
r = Rect(1000, 500)

@test(150)
def test_fit(_r):
    inset = 150
    ri = r.inset(inset, 0)
    out = P([
        P(ri).f(hsl(0.7, a=0.1)),
        (StSt("COLD", co, 500,
            wdth=1, fit=ri.w, annotate=True)
            .fssw(-1, hsl(0.7), 2)
            .align(r))])
    
    assert ri.w == round(out[1].ambit().w)
    assert out[1]._stst.variations["wdth"] == 379

    return out.align(_r).scale(0.25)

@test(120)
def test_style_mod(r):
    style = Style(co, 250, wdth=1, annotate=True)
    a = StSt("CLDTP", style)
    b = StSt("CLDTP", style.mod(wdth=0))
    
    assert a._stst.variations["wdth"] == 1000
    assert b._stst.variations["wdth"] == 0

    return P(a, b).stack(10).scale(0.25).align(r)

@test(150)
def test_fit_height(r):
    style = Style(co, 250, wdth=1, annotate=True)
    a = StSt("CLDTP", style)
    b = StSt("CLDTP", style.mod(fitHeight=300))
    
    assert a._stst.fontSize == 250
    assert b._stst.fontSize == 400

    return P(a, b).stack(10).align(r).scale(0.25)

@test()
def test_kern_pairs(_r):
    style = Style(co, 250, wdth=1, annotate=True)
    a = StSt("CLD", style)
    b = StSt("CLD", style.mod(kp={"C/L":20, "L/D":100}))
    
    assert a[1].ambit().x == 155.75
    assert b[1].ambit().x == 155.75 + 20*(250/1000)
    assert a[2].ambit().x == 273.5
    assert b[2].ambit().x == 273.5 + 20*(250/1000) + 100*(250/1000)

    return P([a, b]).stack(10).fssw(-1, 0, 1).scale(0.5).align(_r)

@test(80)
def test_normalize(_r):
    style = Style("asdf", 100)
    font_path = Path(style.font.path).relative_to(Path(".").absolute())

    assert font_path == Path("src/coldtype/demo/RecMono-CasualItalic.ttf")

    assert style.font.names()[0] == "Rec Mono Casual Italic"
    assert style.font.names()[1] == "Rec Mono Casual"

    if on_mac():
        style = Style("Times", 100)
        assert style.font.path.name == "Times.ttc"
    elif on_windows():
        style = Style("times", 100)
        assert style.font.path.name == "times.ttf"
    
    return StSt("Hello", style).align(_r).f(0)