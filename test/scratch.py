from coldtype.animation import *


easer_ufo = Font(str(Path(__file__).parent.parent.joinpath("coldtype/animation/easers.ufo")))

def render(f):
    curve = DATPen().glyph(easer_ufo["exp_io"])
    y = curve_y(curve, 0.33)
    print(y, ease("eeio", 0.33))
    return
    #for x in range(0, 10):
    #    print(ease("exp_io", x/10))
    #return
    dps = DATPenSet()
    c = DATPen().f(None).s("random").sw(10).glyph(easer_ufo["exp_io"])
    for easer, fn in eases.items():
        if easer != "eeio":
            continue
        dp = DATPen().f(None).s(1, 0, 0.5).sw(10)
        dp.moveTo((0, 0))
        dp2 = DATPen().f(None).s(1, 0.5).sw(20)
        dp2.moveTo((0, 0))
        for x in range(0, 100):
            e = ease(easer, x/100)
            dp.lineTo((x*10, e*1000))
            dp2.lineTo(c.point_t(x/100)[0])
        dp.lineTo((1000, 1000))
        dp.endPath()
        dp2.endPath()
        dps.addPen(dp)
        dps.addPen(dp2.translate(0, 0))
        g = dp.to_glyph(easer)
        #print(g.getPen().contour)
        #easer_ufo.layers["samples"].insertGlyph(g)
    #easer_ufo.save()
    #c = DATPen().f(None).s("random").sw(10).glyph(easer_ufo["exp_io"])
    #c.subsegment(0.5, 1)
    #dps.addPen(c.translate(500, 0))
    return dps.translate(100, 40)

animation = Animation(render)