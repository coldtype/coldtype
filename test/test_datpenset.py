from coldtype.test import *

@test()
def test_distribute_and_track(r):
    dps = DATPens()
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
def test_track_to_rect(r):
    text:DATPens = StyledString("COLD", Style(co, 300, wdth=0, r=1)).pens().align(r)
    return text.track_to_rect(r.inset(50, 0), r=1)


@test()
def test_map_points(r):
    pt_labels = DATPens()
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
    return DATPens([
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