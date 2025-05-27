from coldtype import *

def interrupt_lines(lines:list[Line], rects:list[Rect]):
    out = P()

    for l in lines:
        p = P().m(l.start)

        for rect in rects:
            ra = rect.ambit()
            if l.intersects(ra.ew):
                p1 = l.intersection(ra.ew)
                p2 = l.intersection(ra.ee)
                p.l(p1).ep()
                p.m(p2)
    
        out += p.l(l.end).ep()
    return out

@aframe(bg=1)
def lines(f:Frame):
    s = Scaffold(f.a.r).numeric_grid(10, 10)
    
    rects = (P(
        P(s["3|3"].r.inset(0, -14)),
        P(s["6|4*2|2"].r.inset(0, 14))
    )).fssw(-1, hsl(0.6), 1)

    lines = []

    for x in range(1, 10):
        start, end = s[f"0|{x}"], s[f"9|{x}"]
        lines.append(Line(start.r.psw, end.r.pse))
    
    pts = interrupt_lines(lines, [r.ambit().inset(-8, 0) for r in rects])
    
    return rects + pts.fssw(-1, hsl(0.8), 1)