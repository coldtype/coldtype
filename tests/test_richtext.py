from coldtype.test import *
from coldtype.text.richtext import RichText

f1 = Font.ColdtypeObviously()
f2 = Font.MutatorSans()

@test()
def test_preserve_space(_r):
    r = Rect(1200, 300)
    rt = RichText(r, "HELLO[i] COLDTYPE", dict(
        i=Style(f2, 200, wdth=0, wght=1),
        default=Style(f1, 200, wdth=0))).align(r)

    assert rt[0][0].data("txt") == "COLDTYPE"
    assert rt[0][1].data("txt") == "HELLO "

    assert rt[0][1][0].glyphName == "space"
    assert rt[0][1][-1].glyphName == "H"

    assert rt[0][0][0].glyphName == "E"
    assert rt[0][0][-1].glyphName == "C"

    space_width = rt[0][1][0].ambit(tx=0).w
    assert space_width == 50

    assert rt[0][1].ambit(tx=0).w - space_width > rt[0][1].ambit(tx=1).w
    
    return rt.align(_r).scale(0.5)

@test()
def test_ligature(_r):
    clarette = Font.Find("ClaretteGX.ttf")

    txt = "fi¬joff≤asdf≥"
    r = Rect(1080, 300)
    
    gl = (RichText(r, txt,
        dict(
            default=Style(clarette, 200),
            asdf=Style(clarette, 200, wdth=1)),
        tag_delimiters=["≤", "≥"],
        visible_boundaries=["¶"],
        invisible_boundaries=["¬"])
        .align(r))
    
    assert gl[0][0].data("style_names")[0] == "asdf"
    assert len(gl[0][1].data("style_names")) == 0
    assert gl[0][0][0].glyphName == "f_f"
    assert gl[0][1][0].glyphName == "f_i"
    
    return gl.align(_r).scale(0.5)