from coldtype.test import *

@test((250, 250), solo=0)
def test_contains(r):
    r0 = r.take(150, "SW").offset(10)
    r1 = r.take(50, "NE").offset(-10)
    r2 = r.take(50, "SW").offset(20)
    r3 = r.take(50, "S").take(50, "CX")
    r4 = r.take(50, "W").take(50, "CY")
    r5 = r0.take(50, "NE")
    
    assert r0.contains(r1) == False
    assert r0.contains(r2) == True
    assert r0.contains(r3) == False
    assert r0.contains(r4) == False
    assert r3.contains(r4) == False
    assert (r5 in r0) == True
    
    return P(P(x) for x in [r0,r1,r2,r3,r4,r5]).fssw(-1, 0, 1)

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

@test((250, 250), solo=0)
def test_aspects(r:Rect):
    ri = r.inset(20)

    r45 = ri.fit_aspect(4, 5)
    assert r45.w == 168
    assert r45.h == ri.h

    r54 = ri.fit_aspect(5, 4)
    assert r54.w == ri.w
    assert r54.h == r45.w

    r169 = ri.fit_aspect(16, 9)
    assert r169.w == ri.w
    assert r169.h == 118.125

    return (P(
        P(r45),
        P(r54),
        P(r169),
        )
        .fssw(-1, 0, 1))
