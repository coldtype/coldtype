from coldtype.test import *

@test((250, 250))
def test_fit(r):
    r1 = P(r.take(20, "NE"))
    assert r1.ambit().w == 20
    assert r1.ambit().x == 250-20
    
    rs = (r1.layer(
        1,
        lambda p: p.align(r, "E"),
        lambda p: p.align(r, "SE"),
        lambda p: p.align(r, "S"),
        lambda p: p.align(r, "SW"),
        lambda p: p.align(r, "W"),
        lambda p: p.align(r, "NW"),
        lambda p: p.align(r, "N"),
    ))

    assert len(rs) == 8
    assert rs.ambit().w == 250
    assert rs.ambit().h == 250
    assert rs[3].ambit().y == 0
    assert rs[5].ambit().x == 0
    
    return rs

@test((250, 250), solo=0)
def test_align_text(r):
    txt = (StSt("Hello\nWorld\nLonger Line", Font.RecMono(), 32)
        .xalign(r, "E"))
    
    assert txt[0].ambit().y == pytest.approx(64.8)
    assert txt[1].ambit().y == pytest.approx(32.4)
    assert txt[2].ambit().y == 0

    assert txt[0].ambit().x == pytest.approx(155.98, rel=1e-4)
    assert txt[1].ambit().x == pytest.approx(154.84, rel=1e-4)
    assert txt[2].ambit().x == pytest.approx(40.47, rel=1e-4)

    return txt