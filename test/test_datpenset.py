from coldtype.test import *

@test()
def test_distribute_and_track(r):
    dps = DATPenSet()
    rnd = Random(0)
    for x in range(0, 11):
        dps += (DATPen()
            .rect(Rect(100, 100))
            .f(hsl(rnd.random(), s=0.6))
            .rotate(rnd.randint(-45, 45)))
    return (dps
        .distribute()
        .track(-50)
        .reversePens()
        .understroke(s=0.2).align(r))


@test()
def test_text_on_a_curve(r):
    text:DATPenSet = StyledString("COLDTYPE "*7, Style(co, 64, tu=-50, r=1, ro=1)).pens()
    for glyph in text:
        glyph.f(hsl(random(), s=1, l=0.75))
    oval = DATPen().oval(r.inset(50)).reverse().repeat()
    return text.distributeOnPath(oval).understroke(s=0, sw=5)


@test((1000, 1000))
def test_text_on_a_curve_fit(r):
    circle = DATPen().oval(r.inset(250)).reverse()
    return (StyledString("COLDTYPE COLDTYPE COLDTYPE ",
        Style(co, 100, wdth=1, tu=0, space=500))
        .fit(circle.length())
        .pens()
        .distributeOnPath(circle)
        .f(Gradient.H(circle.bounds(), hsl(0.5, s=0.6), hsl(0.85, s=0.6))))


@test()
def test_track_to_rect(r):
    text:DATPenSet = StyledString("COLD", Style(co, 300, wdth=0, r=1)).pens().align(r)
    return text.trackToRect(r.inset(50, 0), r=1)


@test()
def test_map_points(r):
    pt_labels = DATPenSet()
    def point_mapper(idx, x, y):
        pt_labels.append(StyledString(str(idx),
            Style("assets/NotoSans-Black.ttf", 10, wght=1, wdth=0))
            .pen()
            .translate(x, y))
        if idx in [12, 13, 14, 26, 27, 28]:
            return x-100, y
    e = (StyledString("E",
        Style(co, 500, ro=1, wdth=1))
        .pen()
        .align(r)
        .map_points(point_mapper))
    return e.f(hsl(random())), pt_labels.f(0, 0.5)


@test()
def test_explode(r):
    o = StyledString("O", Style(co, 500, wdth=1)).pen().explode()
    o[1].rotate(90)
    return o.implode().f(hsl(random())).align(r)


@test()
def test_scaleToRect(r):
    return DATPenSet([
        DATPen().oval(r).scaleToRect(r.take(0.5, "mdx").inset(0, 30), False).f(hsl(0.2, a=0.1)),
        (StyledString("SPACEFILLING",
            Style(mutator, 50))
            .pens()
            .align(r)
            .f(hsl(0.8))
            .scaleToRect(r.inset(100, 100), False)),
        (StyledString("SQUASH",
            Style(mutator, 50))
            .pens()
            .align(r)
            .f(hsl(0.5))
            .scaleToWidth(r.w-20)),
        (StyledString("STRETCH",
            Style(mutator, 50))
            .pens()
            .align(r)
            .f(hsl(0.3))
            .scaleToHeight(r.h-50))
    ])

@test()
def test_photoblique(r):
    return (StyledString("OBLQ",
        Style(mutator, 300, wght=0.5))
        .pen()
        .align(r, th=1, tv=1)
        .f(hsl(0.7, a=0.5))
        .s(hsl(0.9, a=1))
        .sw(5)
        .skew(-0.25))