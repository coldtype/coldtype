from coldtype import *
import beziers.path
import beziers.point

@renderable(rstate=1)
def stub(r, rs):
    points = []
    for g in rs.input_history.strokes(lambda g: g.action == "down" and len(g) > 2):
        ps = []
        for p in g:
            ps.append(p.position)
        points.append(ps)
    
    out = DATPenSet()
    for path in points:
        bpp = beziers.path.BezierPath.fromPoints([beziers.point.Point(p.x, p.y) for p in path], error=1000)
        out += DATPen.from_cbp([bpp]).s(0).sw(15).f(None)
    
    if rs.keylayer == Keylayer.Default or True:
        dp = DATPen().f(0)
        for o in out:
            dp.record(o)
        return dp.f(hsl(0.8, a=0.3)).s(0).sw(5)#.color_phototype(r, blur=10, cut=150)
    else:
        return out.f(hsl(0.3, a=0.3))#.color_phototype(r, blur=10, cut=150)