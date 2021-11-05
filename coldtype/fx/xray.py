from coldtype.pens.datpen import P, PS
from coldtype.geometry import Point
from coldtype.color import hsl


def skeletonLookup(self) -> dict:
    m, l, c, cf, q, qf, cbs, qbs = [[] for x in range(8)]
        
    for idx, (mv, pts) in enumerate(self.value):
        pts = [Point(x) for x in pts]
        if mv == "moveTo":
            m.append(pts[0])
        elif mv == "lineTo":
            l.append(pts[0])
        elif mv in ["curveTo", "qCurveTo"]:
            lp = Point(self.value[idx-1][-1][-1])
            pts.insert(0, lp)
            onc = pts[-1]
            if mv == "curveTo":
                c.append(onc)
                cf.extend([pts[1], pts[2]])
                cbs.append([pts[0], pts[1]])
                cbs.append([pts[-2], onc])
            else:
                q.append(onc)
                for j, _p in enumerate(pts[:-2]):
                    np = pts[j+1]
                    qbs.append([_p, np])
                    qf.append(np)
                qbs.append([pts[-2], onc])
    
    return {
        "moveTo": m,
        "lineTo": l,
        "curveOn": c,
        "curveOff": cf,
        "qCurveOn": q,
        "qCurveOff": qf,
        "curveBars": cbs,
        "qCurveBars": qbs
    }


def skeleton(scale=1):
    def _skeleton(p:P):
        pts = list(skeletonLookup(p).values())
        return (PS([
            (PS.E(pts[0],
                lambda x: P().r(x.el.r(30)))
                .tag("moveTo")),
            (PS.E(pts[1],
                lambda x: P().r(x.el.r(20)))
                .tag("lineTo")),
            (PS.E(pts[2],
                lambda x: P().o(x.el.r(20)))
                .tag("curveOn")),
            (PS.E(pts[3],
                lambda x: P().o(x.el.r(10)))
                .tag("curveOff")),
            (PS.E(pts[4],
                lambda x: P().o(x.el.r(20)))
                .tag("qCurveOn")),
            (PS.E(pts[5],
                lambda x: P().o(x.el.r(10)))
                .tag("qCurveOff")),
            (PS.E(pts[6],
                lambda x: P().l(x.el))
                .tag("curveBars")),
            (PS.E(pts[7],
                lambda x: P().l(x.el))
                .tag("qCurveBars")),
            ])
            .ï([0, 1, 2, 3, 4, 5], lambda p:
                p.pmap(lambda x: x.scale(scale)))
            .fssw(-1, 0, 2))
    return _skeleton