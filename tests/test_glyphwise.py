from coldtype.test import *


def _test_glyph_kerning(font_path, kern):
    txt = "AVAMANAV"
    ss = StSt(txt, font_path, 100, wdth=0, kern=kern)
    gw = Glyphwise(txt, lambda g: Style(font_path, 100, wdth=0, kern=kern, ro=1))
    gwo = Glyphwise(txt, lambda g: Style(font_path, 100, wdth=0, kern=(not kern), ro=1))

    assert len(ss) == len(txt)
    assert ss[0].glyphName == "A"
    assert ss[-1].glyphName == "V"
    assert len(gw) == len(txt)
    assert ss[0].glyphName == "A"
    assert ss[-1].glyphName == "V"

    assert ss.ambit() == gw.ambit()
    assert ss.ambit() != gwo.ambit()
    return ss, gw

@test(150)
def test_format_equality(r):
    fnt = "OhnoFatfaceVariable.ttf"
    return (P(
        *_test_glyph_kerning(fnt, False),
        *_test_glyph_kerning(fnt, True))
        .stack()
        .scale(0.5)
        .align(r))

@test(100)
def test_ligature(r):
    clarette = Font.Find("ClaretteGX.ttf")
    gl = (Glyphwise(["fi", "j", "o", "ff"],
        lambda g: Style(clarette, 200, wdth=g.i/3))
        .align(r))
    
    assert len(gl) == 4
    assert gl[0].glyphName == "f_i"
    assert gl[-1].glyphName == "f_f"
    
    #return gl.scale(0.5)

    gl2 = (Glyphwise2("fijoff",
        lambda g: Style(clarette, 200, wdth=g.i/3))
        .align(r))
    
    assert len(gl2) == 4
    assert gl2[0].glyphName == "f_i"
    assert gl2[-1].glyphName == "f_f"

    gl3 = (Glyphwise2("fijoff",
        lambda g: Style(clarette, 200, wdth=g.i/3)
        , multiline=1)
        .align(r))
    
    assert len(gl3) == 1
    assert len(gl3[0]) == 4
    
    return gl2.scale(0.25)

@test(160)
def test_variable_args(r):
    fnt = Font.Find("OhnoFatfaceV")
    out = P()
    
    (Glyphwise("FATFACE 1 ARG", lambda g:
        Style(fnt, 100, wdth=g.e))
        .attach(out))
    
    es = []
    def print_e(g):
        es.append(g.e)
        return Style(fnt, 100, opsz=g.e, wdth=1-g.e)
    
    (Glyphwise("FATFACE 2 ARG", print_e)
        .attach(out))
    
    assert es[0] == 0
    assert es[1] == pytest.approx(0.083333333333)
    assert es[-1] == 1

    return out.stack(10).align(r)

@test()
def test_newline(r):
    _r = Rect(1080, 300)
    fnt = Font.Find("OhnoFatfaceV")
    
    gs = (Glyphwise("FATFACE\nFACEFAT", lambda g:
        Style(fnt, g.i*10+50, wdth=g.e))
        .align(_r))
    
    assert gs[0][0].ambit().xy() == [305.21250000000003, 172.05]
    assert gs[1][-1].ambit().xy() == [656.3775, 58.650000000000006]
    
    assert gs[0][-1].glyphName == "E"
    assert gs[1][-1].glyphName == "T"
    return gs.align(r)

@test(150)
def test_newline_onechar(r):
    fnt = Font.MutatorSans()
    _r = Rect(1080, 300)
    
    gs = (Glyphwise("T\nYPE", lambda g:
        Style(fnt, 150-g.i*20, wdth=1-g.e))
        .xalign(_r)
        .lead(20)
        .align(_r)
        )
    
    assert gs[0][0].ambit().xy() == pytest.approx([454.5, 153.0])
    assert gs[1][-1].ambit().xy() == [629.56, 42.0]
    assert gs[0][0].glyphName == gs[0][-1].glyphName
    assert gs[0][0].glyphName == "T"
    assert gs[1][-2].glyphName == "P"

    return gs.scale(0.5).align(r)

@test()
def test_kp(r):
    fnt = Font.Find("OhnoFatfaceV")
    _r = Rect(1080, 300)

    gs_no_kp = (Glyphwise("FATFACE", lambda g:
        Style(fnt, 250, wdth=1-g.e, ro=1))
        .align(_r)
        .fssw(-1, 0, 1))
    
    gs_kp = (Glyphwise("FATFACE", lambda g:
        Style(fnt, 250, wdth=1-g.e, kp={"A/T":-250}, ro=1))
        .align(_r)
        .fssw(-1, 0, 1))
    
    kp_sw = gs_kp[2].ambit().psw
    no_kp_sw = gs_no_kp[2].ambit().psw

    assert kp_sw != no_kp_sw
    assert kp_sw.y == no_kp_sw.y

    return (P(gs_kp, gs_no_kp)
        .stack(10)
        .align(r)
        .scale(0.5))

@test()
def test_tu(r):
    fnt = Font.Find("OhnoFatfaceV")
    _r = Rect(1080, 300)

    gs_no_tu = (Glyphwise("FATFACE", lambda g:
        Style(fnt, 250, wdth=1-g.e, ro=1))
        .align(_r)
        .fssw(-1, 0, 1))
    
    gs_tu = (Glyphwise("FATFACE", lambda g:
        Style(fnt, 250, wdth=1-g.e, tu=-50, ro=1))
        .align(_r)
        .fssw(-1, 0, 1))

    assert gs_tu.ambit().w < gs_no_tu.ambit().w

    return P(gs_no_tu, gs_tu).stack(10).align(r).scale(0.5)

@test(80)
def test_multistyle(r):
    def styler1(g):
        return Style(Font.MutatorSans(), 100, wdth=0)
    
    def styler2(g):
        return [
            Style(Font.MutatorSans(), 100, wdth=0),
            Style(Font.MutatorSans(), 100, wdth=g.e),
        ]
    
    g1 = (Glyphwise("ASDF", styler1)
        .fssw(-1, 0, 1))
    
    g2 = (Glyphwise("ASDF", styler2)
        .fssw(-1, 0, 1))
    
    assert g1.ambit().w == g2.ambit().w
    assert g1.ambit(tx=1).w != g2.ambit(tx=1).w

    assert g1[-1].glyphName == "F"
    assert g2[-1].glyphName == "F"
    assert g2[-1].data("frame").w == g1[-1].data("frame").w
    assert g1[-1].ambit(tx=1).w == 28.0
    assert g2[-1].ambit(tx=1).w == 86.0

    return P(g1, g2).distribute().track(100).align(r).scale(0.5)

@test(150)
def test_multiline(r):
    def styler(g):
        return Style(Font.MutatorSans(), 120,
            meta=dict(idx=g.i))
    
    gw = (Glyphwise("AB\nCD\nEF", styler))

    assert len(gw) == 3
    gw.collapse()
    assert len(gw) == 6

    for idx, g in enumerate(gw):
        assert g.data("idx") == idx

    gw2 = (Glyphwise("ABC", styler, multiline=1))
    
    assert len(gw2) == 1
    gw2.collapse()
    assert len(gw2) == 3

    for idx, g in enumerate(gw2):
        assert g.data("idx") == idx
    
    gw3 = (Glyphwise("ABC", styler, multiline=0))
    assert len(gw3) == 3
    gw3.collapse()
    assert len(gw3) == 3

    for idx, g in enumerate(gw3):
        assert g.data("idx") == idx
    
    return (P(gw, gw2, gw3)
        .distribute()
        .track(20)
        .align(r)
        .scale(0.5))

@test(10)
def test_no_reverse(r):
    def styler(g):
        return Style(Font.MutatorSans(), 120, r=1)
    
    with pytest.raises(Exception) as context:
        (Glyphwise("AB\nCD\nEF", styler))
    
    assert "r=1 not possible" in str(context.value)
    return None

@test(100)
def test_multistyle_stst(r):
    stst = (StSt("COLD\nCOLD", [
        Style(Font.MuSan(), 30, wght=1),
        Style(Font.ColdObvi(), 40, wght=1)])
        .xalign(r)
        .align(r))
    
    assert stst[0][0].glyphName == "C"
    assert stst[-1][-1].glyphName == "D"

    print(len(stst[0][0]._val.value))
    assert len(stst[0][0]._val.value) == 32
    assert len(stst[1][0]._val.value) == 32
    
    return stst