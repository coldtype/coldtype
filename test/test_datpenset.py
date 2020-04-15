from coldtype.test import *

@test()
def test_distribute_and_track(r):
    dps = DATPenSet()
    rnd = Random(0)
    for x in range(0, 11):
        dps += DATPen().rect(Rect(100, 100)).f("hr",0.65,0.55).rotate(rnd.randint(-45, 45))
    return dps.distribute().track(-50).reversePens().understroke(s=0.2).align(r)


@test()
def test_text_on_a_curve(r):
    text:DATPenSet = StyledString("COLDTYPE "*7, Style(co, 64, tu=-50, r=1, ro=1)).pens().f("hr",0.5,0.75)
    oval = DATPen().oval(r.inset(50)).reverse().repeat()
    return text.distributeOnPath(oval).understroke(s=("hr",0.5, 0.15), sw=5)


@test()
def test_track_to_rect(r):
    text:DATPenSet = StyledString("COLD", Style(co, 300, wdth=0, r=1)).pens().align(r)
    return text.trackToRect(r.inset(50, 0), r=1)


@test()
def test_map_points(r):
    pt_labels = DATPenSet()
    def point_mapper(idx, x, y):
        pt_labels.append(StyledString(str(idx), Style("assets/NotoSans-Black.ttf", 10, wght=1, wdth=0)).pen().translate(x, y))
        if idx in [12, 11, 10, 9, 24, 23, 22, 21]:
            return x-100, y
        #elif idx in [7, 6]:
        #    return x+50, y
    e = StyledString("E", Style(co, 500, ro=1, wdth=1)).pen().align(r).map_points(point_mapper)
    return e.f("hr",0.75,0.75), pt_labels.f(0, 0.5)


@test()
def test_explode(r):
    o = StyledString("O", Style(co, 500, wdth=1)).pen().explode()
    o[1].rotate(90)
    return o.implode().f("hr",0.75,0.35).align(r)


