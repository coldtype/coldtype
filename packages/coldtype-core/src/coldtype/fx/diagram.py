from coldtype.runon.path import P
from coldtype.geometry.rect import Rect, txt_to_edge


def arrowhead(pt, arrow, x=18, y=13):
    ah = P().m(pt)
    if arrow == "←":
        ah.l(pt.o(x, y)).l(pt.o(x, -y)).t(-7, 0)
    elif arrow == "→":
        ah.l(pt.o(-x, y)).l(pt.o(-x, -y)).t(7, 0)
    elif arrow == "↓":
        ah.l(pt.o(-y, x)).l(pt.o(y, x)).t(0, -7)
    elif arrow == "↑":
        ah.l(pt.o(-y, -x)).l(pt.o(y, -x)).t(0, 7)
    ah.cp().f(0)#.fssw(0, 1, 1.5)
    return ah


def connection(a, b, spec="→←"):
    start = spec[0]
    end = spec[1]
    arrow = spec[2] if len(spec) > 2 else None
    corner = spec[3] if len(spec) > 3 else None

    src = a.ambit().point(start)
    dst = b.ambit().point(end)
    if src.x == dst.x or src.y == dst.y:
        line = P().m(src).l(dst)
    else:
        corn = Rect.FromPoints(src, dst).point(corner)
        line = P().m(src).l(corn).l(dst)
    line.ep().fssw(-1, 0, 2)
    lines = P()
    lines.append(line)
    if arrow is not None:
        ar = dst #line.ambit().point(arrow)
        lines.insert(0, arrowhead(ar, arrow))
    return lines


def interconnect(spec="→←→"):
    def _interconnect(ps):
        lines = P()
        for idx, p in enumerate(ps[:-1]):
            lines += connection(p, ps[idx+1], spec)
        return ps.append(lines)
    return _interconnect


def ujoin(a, b, side="→", d=100, arrow=None):
    a_pt = a.ambit().point(side)
    b_pt = b.ambit().point(side)
    ab = Rect.FromPoints(a_pt, b_pt).expand(d, txt_to_edge(side))
    l = ab.edge(txt_to_edge(side))
    
    bar = P()
    if side in "←→":
        if a_pt.y < b_pt.y:
            bar.m(a_pt).l(l.ps).l(l.pn).l(b_pt).ep()
        else:
            bar.m(b_pt).l(l.ps).l(l.pn).l(a_pt).ep()
    
    out = P()
    if arrow:
        if len(arrow) > 1:
            a_arrow = arrow[0]
            b_arrow = arrow[1]
        else:
            a_arrow, b_arrow = arrow, arrow
        if a_arrow != "-":
            out.insert(0, arrowhead(a_pt, a_arrow))
        if b_arrow != "-":
            out.insert(0, arrowhead(b_pt, b_arrow))
    return out.append(bar.fssw(-1, 0, 2))