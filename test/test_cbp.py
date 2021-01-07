from coldtype import *
import beziers.path
import beziers.point
import glfw
from defcon import Font

ufo = Font(str(__sibling__("media/test_draw.ufo")))
#ufo.save()

@renderable(rstate=1)
def stub(r, rs):
    all_points = [[]]
    for g in rs.input_history.strokes(lambda g: g.action in ["down", "cmd"] and len(g) > 2):
        if g.action == "cmd":
            if g.position() == glfw.KEY_B:
                all_points.append([])
            continue
        ps = []
        for p in g:
            ps.append(p.position)
        all_points[-1].append(ps)

    dps = DATPenSet()
    for points in all_points:
        out = DATPenSet()
        for path in points:
            bpp = beziers.path.BezierPath.fromPoints([beziers.point.Point(p.x, p.y) for p in path], error=1000).smooth().addExtremes()
            out += DATPen.from_cbp([bpp]).s(0).sw(15).f(None)
        
        #dp = DATPen().f(0).record(out).connect()
        #dp.filter(lambda i, mv, ps: mv not in ["endPath"])
        dp = out.pen()
        try:
            dp.value[-1] = ("closePath", [])
        except IndexError:
            pass
        dps += dp
        #dps += out.pen()
    
    if rs.keylayer == Keylayer.Default:
        return dps.pen().f(0).s(0).sw(5).color_phototype(r, blur=5, cut=150)
    else:
        #print(len(dps.pen().value))
        if rs.cmd == "save":
            from pprint import pprint
            pprint(dps.pen().value)
            g = dps.pen().to_glyph()
            ufo.insertGlyph(g, name="N")
            ufo.save()
        return [
            dps.pen().f(0).s(0).sw(5).color_phototype(r, blur=5, cut=150),
            dps.f(None).s(hsl(0.9, s=1, l=0.8)).sw(2),
            dps.pen().skeleton()
        ]