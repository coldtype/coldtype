from coldtype.test import *

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
mutator = Font.Cacheable("assets/MutatorSans.ttf")

@test()
def test_scaleToRect(_r):
    r = Rect(1000, 500)
    dps = P([
        (StSt("SPACEFILLING", mutator, 50)
            .align(r)
            .f(hsl(0.8))
            .scaleToRect(r.inset(100, 100), False)),
        (StSt("SPACEFILLING", mutator, 50)
            .align(r)
            .f(hsl(0.5))
            .scaleToWidth(r.w-20)),
        (StSt("SPACEFILLING", mutator, 50)
            .align(r)
            .f(hsl(0.3))
            .scaleToHeight(r.h-50))])
    
    assert dps[0].ambit(tx=1).w == pytest.approx(r.inset(100).w)
    assert dps[0].ambit(ty=1).h == pytest.approx(r.inset(100).h)
    assert dps[1].ambit(tx=1).w == pytest.approx(r.w-20)
    assert dps[2].ambit(ty=1).h == r.h-50
    
    return dps.align(_r).scale(0.5)

@test(100)
def test_distribute_and_track(_r):
    dps = P()
    rnd = Random(0)
    r = Rect(1000, 500)

    for _ in range(0, 11):
        dps += (P()
            .rect(Rect(100, 100))
            .f(hsl(rnd.random(), s=0.6))
            .rotate(rnd.randint(-45, 45)))
    dps = (dps
        .distribute()
        .track(-50)
        .reverse()
        .understroke(s=0.2)
        .align(r)
        )
    
    assert len(dps) == 11
    assert dps.ambit(tx=1).round().w == 830

    return dps.align(_r).scale(0.5)

@test()
def test_track_to_rect(_r):
    r = Rect(1000, 500)
    text = (StSt("COLD", co, 300, wdth=0, r=1)
        .align(r)
        .track_to_rect(r.inset(50, 0), r=1))
    
    assert text[0].glyphName == "D"
    assert text[-1].ambit().round().x == 50
    assert text[0].ambit().round().x == 883

    return text.align(_r).scaleToRect(_r.inset(10))

@test()
def test_distribute_oval(_r):
    r = Rect(1000, 500)
    txt = (StSt("COLDTYPE "*7, co, 64,
        tu=-50, r=1, ro=1)
        .distribute_on_path(P()
            .oval(r.inset(50))
            .reverse()
            .repeat())
        .fssw(hsl(0.9), 0, 3, 1))

    assert len(txt) == 62
    
    x, y = txt[-1].ambit().xy()
    assert round(x) == 500
    assert round(y) == 50

    txt.unframe().align(_r).scale(0.35, point=_r.pc)

    return (P(
        P(txt.ambit()).f(hsl(0.3, 1)),
        txt))

@test()
def test_distribute_path_lines(_r):
    r = Rect(1080, 1080).inset(200)
    p = (P().m(r.psw).l(r.pn).l(r.pse).ep())

    lockup = (StSt("COLDTYPE",
        Font.MutatorSans(), 220, wght=.4, wdth=0.5)
        .distribute_on_path(p)
        .align(r, ty=1, tx=1)
        .f(0))

    x, y = lockup[3].ambit().xy()

    assert lockup[3].glyphName == "D"
    assert round(x) == 454
    assert round(y) == 690

    x, y = lockup[-1].ambit().xy()

    assert lockup[-1].glyphName == "E"
    assert round(x) == 792
    assert round(y) == 312

    return P(p, lockup).align(_r).scale(0.25)

@test()
def test_stack(_r):
    sr = Rect(100, 100)

    res = (P(
        P().oval(sr).f(hsl(0.5)).tag("A"),
        P().oval(sr).f(hsl(0.7)).tag("B"),
        P().oval(sr).f(hsl(0.9)).tag("C"))
        .stack(10))

    assert res.find_("C").ambit().y == 0
    assert res.find_("B").ambit().y == 110
    assert res.find_("A").ambit().y == 220

    return res.align(_r).scale(0.5)

@test()
def test_stack_and_lead(_r):
    sr = Rect(100, 100)

    res = (P(
        P().oval(sr).f(hsl(0.5)).tag("A"),
        P().oval(sr).f(hsl(0.7)).tag("B"),
        P().oval(sr).f(hsl(0.9)).tag("C"))
        .stack(10)
        .lead(10))

    assert res.find_("C").ambit().y == 0
    assert res.find_("B").ambit().y == 120
    assert res.find_("A").ambit().y == 240

    return res.align(_r).scale(0.5)

@test((800, 150))
def test_projection(r):
    return (P().rect((300, 300))
        .difference(P().rect((-150, -150, 300, 300)))
        .layer(
            λ.castshadow(-35, 200).f(hsl(0.1, 1)),
            λ.project(-35, 200).f(hsl(0.9, 0.8)),
            λ.f(hsl(0.3, 0.6)))
        .align(r)
        .scale(0.25))

@test((800, 150))
def test_plural_boolean(r):
    r = r.square()
    res = (P(
        P(r),
        P().oval(r.inset(10)),
        P().oval(r.inset(20)))
        .intersection()
        .f(0))

    assert res.ambit() == r.inset(20)
    
    return res

@test((800, 150))
def test_gridlayer(r):
    res = (P().rect(Rect(30, 30))
        .gridlayer(3, 3, 10, 10)
        .align(r))
    
    res2 = (P().rect(Rect(30, 30))
        .layer(3)
        .spread(10)
        .layer(3)
        .stack(10)
        .align(r))
    
    assert res.ambit() == res2.ambit()
    
    assert len(res) == 3
    assert len(res[0]) == 3
    assert len(res[0][0]) == 0
    assert len(res[0][0]._val.value) == 5

    res.mapvch(lambda b, p: p.f(hsl(0.65 if b else 0.85)))

    assert res[0][0].f().h/360 == pytest.approx(0.85)
    assert res[0][1].f().h/360 == pytest.approx(0.65)

    res.mapvrc(lambda r, c, p: p.rotate(45 if r == 1 and c == 1 else 0))

    assert res[0][0].ambit().w == res[0][1].ambit().w
    assert res[1][0].ambit().w != res[1][1].ambit().w # the rotated one has a bigger ambit
    assert res[2][0].ambit().w == res[2][1].ambit().w

    return res