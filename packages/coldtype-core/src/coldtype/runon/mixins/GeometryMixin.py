from coldtype.geometry.point import Point
from coldtype.geometry.line import Line


class GeometryMixin():
    def nsew(self):
        pts = [el[1][-1] for el in self.v.value if len(el[1]) > 0]
        
        lines = []
        for i, p in enumerate(pts):
            if i + 1 == len(pts):
                lines.append(Line(p, pts[0]))
            else:
                lines.append(Line(p, pts[i+1]))
        
        mnx, mny, mxx, mxy = self.bounds().mnmnmxmx()
        min_ang = min([l.ang for l in lines])
        max_ang = max([l.ang for l in lines])
        #for idx, l in enumerate(lines):
        #    print(idx, ">", l.ang, min_ang, max_ang)
        xs = [l for l in lines if l.ang < 0.25 or l.ang > 2.5]
        ys = [l for l in lines if 1 < l.ang < 2]

        if len(ys) == 2 and len(xs) < 2:
            xs = [l for l in lines if l not in ys]
        elif len(ys) < 2 and len(xs) == 2:
            ys = [l for l in lines if l not in xs]
        
        #for l in ys:
        #    print(l.ang)

        #print(len(xs), len(ys))
        #print("--------------------")

        try:
            n = [l for l in xs if l.start.y == mxy or l.end.y == mxy][0]
            s = [l for l in xs if l.start.y == mny or l.end.y == mny][0]
            e = [l for l in ys if l.start.x == mxx or l.end.x == mxx][0]
            w = [l for l in ys if l.start.x == mnx or l.end.x == mnx][0]
            return n, s, e, w
        except IndexError:
            amb = self.ambit(tx=1, ty=1)
            return [amb.en, amb.es, amb.ee, amb.ew]
        
    
    def avg(self):
        self.pvl()
        pts = []
        for _, _pts in self.v.value:
            if len(_pts) > 0:
                pts.extend(_pts)
        n = len(pts)
        return Point(
            sum([p.x for p in pts])/n,
            sum([p.y for p in pts])/n)

    @property
    def ecx(self):
        n, s, e, w = self.nsew()
        return e.interp(0.5, w.reverse())
    
    @property
    def ecy(self):
        n, s, e, w = self.nsew()
        return n.interp(0.5, s.reverse())
    
    def edge(self, e):
        e = e.lower()
        if e == "n":
            return self.en
        elif e == "s":
            return self.es
        elif e == "e":
            return self.ee
        elif e == "w":
            return self.ew

    def point(self, pt):
        n, s, e, w = self.nsew()
        if pt == "NE":
            return n.pe
        elif pt == "NW":
            return n.pw
        elif pt == "SE":
            return s.pe
        elif pt == "SW":
            return s.pw
        elif pt == "N":
            return n.mid
        elif pt == "S":
            return s.mid
        elif pt == "E":
            return e.mid
        elif pt == "W":
            return w.mid
        elif pt == "C":
            return self.ecx.sect(self.ecy)

    @property
    def pne(self): return self.point("NE")
    @property
    def pnw(self): return self.point("NW")
    @property
    def psw(self): return self.point("SW")
    @property
    def pse(self): return self.point("SE")
    @property
    def pn(self): return self.point("N")
    @property
    def ps(self): return self.point("S")
    @property
    def pe(self): return self.point("E")
    @property
    def pw(self): return self.point("W")
    @property
    def pc(self): return self.point("C")
    @property
    def en(self): return self.nsew()[0]
    @property
    def es(self): return self.nsew()[1]
    @property
    def ee(self): return self.nsew()[2]
    @property
    def ew(self): return self.nsew()[3]