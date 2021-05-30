from coldtype import *
from more_itertools import split_at
from glfw import KEY_B, KEY_C
import pickle

saved_history = __sibling__("_test_drawing_history.pickle")

@renderable((1500, 1500), rstate=1)
def stub(r, rs):
    history = rs.input_history
    history = pickle.load(saved_history.open("rb"))

    pts = []
    for g in history.strokes(lambda g: g.action in ["down", "cmd"] and g.keylayer == Keylayer.Editing):
        if g.action == "cmd":
            pts.append(g.items[0].position)
        else:
            pts.append(g.items[0].position.round_to(10))
    
    dps = DATPenSet()
    dp = DATPen()
    highlights = DATPenSet()
    aligns = DATPenSet()

    for idx, seg in enumerate(split_at(pts, lambda x: x in [KEY_C], keep_separator=True)):
        if len(seg) == 0:
            continue
        elif seg[0] == KEY_C:
            dp.closePath()
            dps.append(dp)
            dp = DATPen()
        else:
            for idx, pt in enumerate(seg):
                if isinstance(pt, Point):
                    aligns += DATPen().line([[0, pt.y], [r.w, pt.y]]).s(hsl(0.5, a=0.5)).sw(4)
                    aligns += DATPen().line([[pt.x, 0], [pt.x, r.h]]).s(hsl(0.5, a=0.5)).sw(4)
            #print(seg)
            for idx, pt in enumerate(seg):
                if pt == KEY_B:
                    last_on = dp.value[-3][-1][-1]
                    curve_on = dp.value[-1][-1][0]
                    cp = dp.value[-2][-1][0]
                    dp.value = dp.value[:-2]
                    if False:
                        highlights.append(
                            (DATPen()
                            .oval(last_on.rect(30, 30)))
                            .f(hsl(0.2, s=1, a=0.75))
                            .s(0))
                    dp.curveTo(
                        last_on.interp(0.85, cp),
                        curve_on.interp(0.85, cp),
                        curve_on)
                else:
                    dp.lineTo(pt)
    dps.append(dp)

    if rs.cmd == "save":
        pickle.dump(rs.input_history, saved_history.open(mode="wb"))

    if rs.keylayer == Keylayer.Editing:
        if rs.mouse:
            pt = rs.mouse.round_to(10)
            aligns += DATPen().line([[0, pt.y], [r.w, pt.y]]).s(hsl(0.5, s=1, a=0.5)).sw(6)
            aligns += DATPen().line([[pt.x, 0], [pt.x, r.h]]).s(hsl(0.5, s=1, a=0.5)).sw(6)
            aligns += DATPen().oval(pt.rect(30, 30)).f(None).s(hsl(0.3, s=1)).sw(5)
        return [
            DATPen().rect(r.take(250, "mny")).f(0, 0.3),
            DATPen().rect(r).f(None).s(hsl(0.7)).sw(15),
            dps.f(None).s(hsl(0.9, s=1)).sw(15),
            dps.pen().skeleton().f(None).s(hsl(0.3, s=1)).sw(3),
            #DATPen().rect(rs.mouse.round_to(10).rect(10, 10)).f(hsl(0.5, s=1, a=0.75)) if rs.mouse else None,
            highlights,
            aligns
        ]
    else:
        return [
            DATPen().rect(r).f(1, 0.75),
            dps.pen().f(hsl(0.5, a=0.75))
        ]