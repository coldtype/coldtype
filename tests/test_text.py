from coldtype.test import *

tf = Path(__file__).parent

def _test_glyph_names(r, font_path):
    ss = StSt("CDELOPTY", font_path, 300, wdth=0).align(r)
    assert len(ss) == 8
    assert ss[0].glyphName == "C"
    assert ss[-1].glyphName == "Y"
    return ss

@test((800, 150))
def test_format_equality(r):
    _r = Rect(800, 300)

    ttf = _test_glyph_names(_r, Font.ColdtypeObviously())
    otf = _test_glyph_names(_r, "assets/ColdtypeObviously_CompressedBlackItalic.otf")
    ufo = _test_glyph_names(_r, "assets/ColdtypeObviously_CompressedBlackItalic.ufo")
    ds = _test_glyph_names(_r, "assets/ColdtypeObviously.designspace")

    # TODO why isn't the ttf version equal to these?
    assert ufo[0].v.value == ds[0].v.value
    assert ufo[-1].v.value == ds[-1].v.value

    return P([
        ttf, otf, ufo, ds
    ]).fssw(-1, hsl(0.5, a=0.1), 3).scale(0.5).align(r)

@test((800, 100))
def test_space(r):
    _r = Rect(2000, 1000)

    txt = StSt("A B", Font.MutatorSans(), 1000)
    space = txt[1]
    assert space.glyphName == "space"
    assert space.ambit().w == 250
    assert txt.ambit().w == 1093
    assert space.ambit().x == 400
    txt.align(_r, tx=1)
    assert space.ambit().x == 863.5

    txt = StSt("A B", Font.MutatorSans(), 1000, space=500)
    space = txt[1]
    assert space.glyphName == "space"
    assert space.ambit().w == 500
    assert txt.ambit().w == 1093+250
    assert space.ambit().x == 400
    txt.align(_r, tx=1)
    assert space.ambit().x == 863.5-(250/2)

    return txt.scale(0.1).align(r)

@test((800, 100))
def test_static_fonts(r):
    _r = Rect(1200, 300)
    f1 = Font.ColdtypeObviously()
    co = (StSt("CDELOPTY", f1, 200)
        .align(_r))
    
    assert co.ambit(tx=0).w == pytest.approx(998.8)
    assert co.ambit(tx=1).w == pytest.approx(1018.8, 1)
    assert len(co) == 8
    assert f1.font.fontPath.stem == "ColdtypeObviously-VF"

    return co.align(r).scale(0.5)

@test((800, 100))
def test_color_font(r):
    txt = StSt("C", "PappardelleParty-VF.ttf", 100, palette=2)
    assert len(txt) == 1
    assert len(txt[0]) == 3
    assert txt[0][0].glyphName == "C_layer_0"
    assert txt[0][-1].glyphName == "C_layer_2"
    assert txt[0][0].f().h == pytest.approx(176.666, 2)

    txt = StSt("COLDTYPE", "PappardelleParty-VF.ttf", 100)
    assert txt[0][0].f().h == pytest.approx(196.318, 2)

    return txt.align(r)

@test((800, 150))
def test_narrowing_family(r):
    _r = Rect(1080, 300)
    style = Style("Nikolai-Bold.otf", 200, narrower=Style("Nikolai-NarrowBold.otf", 200, narrower=Style("Nikolai-CondBold.otf", 200)))

    out = P()

    txt = StSt("Narrowing", style, fit=_r.w)
    assert int(txt.ambit().w) == 928
    out.append(txt.align(r))

    txt = StSt("Narrowing", style, fit=_r.w-200)
    assert int(txt.ambit().w) == 840
    out.append(txt.align(r))

    txt = StSt("Narrowing", style, fit=_r.w-400)
    assert int(txt.ambit().w) == 733
    out.append(txt.align(r))

    txt = StSt("Narrowing", style, fit=_r.w-600)
    assert int(txt.ambit().w) == 733
    out.append(txt.align(r))

    return out.stack(10).scale(0.25).align(r)

@test((800, 150))
def test_unstripped_text(r):
    st1 = StSt("HELLO\n", Font.MutatorSans(), 100, strip=True)
    assert len(st1) == len("HELLO")
    st2 = StSt("HELLO\n", Font.MutatorSans(), 100)
    assert len(st2) == 2
    st3 = st2.collapse().deblank()
    assert len(st3) == len(st1)
    st4 = StSt("\n\nHELLO\n", Font.MutatorSans(), 100, strip=True)
    assert len(st4) == len("HELLO")
    st5 = StSt("\n\nHEL\nL\nO\n", Font.MutatorSans(), 100, strip=True)
    assert len(st5) == 3

    return st5.scale(0.5).align(r)

@test((800, 10))    
def test_zero_font_size(r):
    s = Style(Font.ColdtypeObviously(), 0)
    assert s.fontSize == 0

    s = Style(Font.ColdtypeObviously(), -1)
    assert s.fontSize == 0

    s = Style(Font.ColdtypeObviously(), -1000)
    assert s.fontSize == 0

    st = StSt("COLD", Font.ColdtypeObviously(), 0)
    assert len(st) == 4
    assert st[0].glyphName == "C"
    assert st[-1].glyphName == "D"

    return None

@test((800, 120))
def test_strict_multiline_stst(r):
    out = P()

    st = (StSt("COLD", Font.ColdtypeObviously(), 100,
        multiline=1)
        .attach(out))
    
    assert len(st) == 1
    assert len(st[0]) == 4

    st = (StSt("COLD\nTYPE", Font.ColdtypeObviously(), 100,
        multiline=1).attach(out))
    
    assert len(st) == 2
    assert len(st[1]) == 4

    st = (StSt("COLD\nTYPE", Font.ColdtypeObviously(), 100,
        multiline=0).attach(out))
    
    assert len(st) == 2
    assert len(st[1]) == 4

    return (out.distribute().track(10)
        .map(lambda i,p: p.f(hsl(i*0.2)))
        .scale(0.5)
        .align(r))
    
@test((800, 80))
def test_depth(r):
    out = P()

    st = (StSt("These are some words", Font.RecursiveMono())).attach(out)
    assert st.depth() == 1

    st = (StSt("These are some words", Font.RecursiveMono(), multiline=1)).attach(out)
    assert st.depth() == 2

    st = P([(StSt("These are some words", Font.RecursiveMono(), multiline=1))]).attach(out)
    assert st.depth() == 3

    st = (StSt("These are some words\nbut now on multiple lines\nisn't that interesting", Font.RecursiveMono())).attach(out)
    assert st.depth() == 2

    return (out
        .distribute()
        .track(10)
        .align(r)
        .scale(0.5)
        .map(lambda i,p: p.f(hsl(i*0.2))))

@test((800, 100), solo=1)
def test_word_splitting(r):
    st = (StSt("These are some words", Font.RecursiveMono()))

    assert st.depth() == 1
    assert st[0].glyphName == 'T'
    assert len(st) == 20

    st = st.wordPens(consolidate=True)

    assert st.depth() == 1
    assert st[0].data("word") == 'T/h.italic/e.italic/s.italic/e.italic'
    
    assert len(st) == 4
    
    st = (StSt("These are some words", Font.RecursiveMono(), multiline=1))

    assert st.depth() == 2
    assert st[0][0].glyphName == 'T'
    assert len(st[0]) == 20

    st = st.wordPens(consolidate=True)
    assert st.depth() == 2
    assert st[0][0].data("word") == 'T/h.italic/e.italic/s.italic/e.italic'
    assert len(st[0]) == 4

    st = (StSt("These are\nsome words", Font.RecursiveMono()))

    assert st.depth() == 2
    assert st[0][0].glyphName == 'T'
    assert len(st[0]) == 9

    st = st.wordPens(consolidate=True)
    assert st.depth() == 2
    assert st[-1][-1].data("word") == 'w.italic/o/r.italic/d.italic/s.italic'
    assert len(st[0]) == 2

    return st.align(r)