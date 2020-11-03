from coldtype import *
#from fontTools.pens.pointPen import SegmentToPointPen
from fontPens.digestPointPen import DigestPointPen
import pickle

# TODO encapsulate this kind of thing as a pattern for easily editing vectors?

op = sibling(__file__, "oval.pickle")
if not op.exists():
    oval = (StyledString("L",
        Style("assets/ColdtypeObviously-VF.ttf", 1000))
        .pen()
        .align(Rect(0, 0, 1080, 1080))
        .f(hsl(0.85)))
    pickle.dump(oval, open(op, "wb"))

def listit(t):
    return list(map(listit, t)) if isinstance(t, (list, tuple)) else t

@renderable(rstate=1)
def test_kb(r, rs):
    if not hasattr(rs, "selected"):
        rs.selected = 0

    p = pickle.load(open(op, "rb"))
    p.value = listit(p.value)
    
    if rs.cmd:
        if rs.cmd.startswith("s"):
            rs.selected = int(rs.cmd.split(" ")[1])
        elif rs.cmd.startswith("sc"):
            p.scale(float(rs.cmd.split(" ")[1]))
    
    out = DATPenSet([p.f(hsl(0.6, a=0.3))])

    if rs.keylayer > 0:
        pt_lookup = []

        vi = 0
        ii = 0
        while vi < len(p.value):
            pv = p.value[vi]
            pvpts = p.value[vi][-1]
            for i, pt in enumerate(p.value[vi][-1]):
                pt_lookup.append([vi, ii, i, pt])
                ii += 1
            vi += 1

        if rs.arrow and rs.xray:
            if rs.arrow[0]:
                rs.selected += rs.arrow[0]
            if rs.selected >= len(pt_lookup):
                rs.selected = 0
            if rs.selected < 0:
                rs.selected = len(pt_lookup) - 1
        
        for vi, ii, i, pt in pt_lookup:
            if ii == rs.selected:
                if rs.arrow and not rs.xray:
                    pt[0] += rs.arrow[0]
                    pt[1] += rs.arrow[1]
                    p.value[vi][-1][i] = pt
                #print(vi, ii, i, pt, p.value[vi][-1])
                pt = p.value[vi][-1][i]
                out += (DATPen()
                    .oval(Rect(pt[0]-50, pt[1]-50, 100, 100))
                    .f(None)
                    .s(hsl(0.65, s=1, l=0.65, a=1 if rs.xray else 0.25))
                    .sw(10 if rs.xray else 1))
            if rs.xray:
                out += (DATPen()
                    .oval(Rect(pt[0]-10, pt[1]-10, 20, 20))
                    .f(hsl(0.95 if ii == rs.selected else 0.75, a=0.5))
                    .scale(1.5 if ii == rs.selected else 1))
    
    pickle.dump(p, open(op, "wb"))
    if rs.keylayer == 2:
        p.s(0).sw(2)
    return out

def release(_):
    op.unlink()