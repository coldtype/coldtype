import re, math
from coldtype.geometry import Rect, Edge, Point
from string import ascii_lowercase


def parse_line(d, line):
    parts = re.split(r"\s", line.strip())
    reified = []
    for p in parts:
        if p == "auto" or p == "a":
            reified.append("auto")
        elif "%" in p:
            reified.append(float(p.replace("%", ""))/100 * d)
        else:
            fp = float(p)
            
            reified.append(fp)
    remaining = d - sum([0 if r == "auto" else r for r in reified])
    if not float(remaining).is_integer():
        remaining = round(remaining)
        #raise Exception("floating parse")
    auto_count = reified.count("auto")
    if auto_count > 0:
        auto_d = remaining / auto_count
        auto_ds = [auto_d] * auto_count
        if not auto_d.is_integer():
            auto_d_floor = math.floor(auto_d)
            leftover = remaining - auto_d_floor * auto_count
            for aidx, ad in enumerate(auto_ds):
                if leftover > 0:
                    auto_ds[aidx] = auto_d_floor + 1
                    leftover -= 1
                else:
                    auto_ds[aidx] = auto_d_floor
            #print(auto_ds)
            #print("NO", auto_d - int(auto_d))
    res = []
    for r in reified:
        if r == "auto":
            res.append(auto_ds.pop())
        else:
            res.append(r)
    return res
    #return [auto_d if r == "auto" else r for r in reified]


def union_rect(r1, r2):
    ox = min(r1.x, r2.x)
    oy = min(r1.y, r2.y)
    ex = max(r1.x+r1.w, r2.x+r2.w)
    ey = max(r1.y+r1.h, r2.y+r2.h)
    return Rect(ox, oy, ex-ox, ey-oy)
    
class Grid():
    def __init__(self,
        r,
        columns="auto",
        rows="auto",
        areas=None,
        warn_float=True,
        forcePixel=False,
        ):
        self._rect = r
        self.warn_float = warn_float
        self.force_pixel = forcePixel

        if isinstance(columns, str):
            self.columns = columns
        else:
            self.columns = ("a "*columns).strip()

        if isinstance(rows, str):
            self.rows = rows
        else:
            self.rows = ("a "*rows).strip()
        
        self.areas = areas
        if not self.areas:
            ls = ascii_lowercase
            cs = []
            cw = len(re.sub(r"\s", "", self.columns))
            if len(self.rows) == 1:
                cs = [" ".join(ls[0:cw])]
            else:
                for ridx, r in enumerate(re.sub(r"\s", "", self.rows)):
                    #print("ROW", r, li, ls[li:cw+li])
                    pre = ls[ridx]
                    cs.append(pre + f" {pre}".join(ls[0:cw]))
            self.areas = " / ".join(cs)
            #print(self.areas)

        self.cells = None
        self.keyed = None
        self.update()
    
    def __repr__(self):
        return f"Grid({list(self.keyed.keys())})"
    
    def clone(self, other_grid):
        self.columns = other_grid.columns
        self.rows = other_grid.rows
        self.areas = other_grid.areas
        return self
    
    @property
    def r(self):
        return self.rect
    
    @property
    def rect(self):
        return self._rect
    
    @rect.setter
    def rect(self, rect):
        self._rect = rect
        self.update()
        return self

    def key(self):
        if isinstance(self._rect, str):
            return self._rect
    
    def update(self):
        if self.key():
            return

        # TODO should be read from a configurable dict
        # (on a subclass of grid?)
        self.columns = self.columns.replace("$CLH", "36")
        self.rows = self.rows.replace("$CLH", "36")

        cg, bs = self.calc_grid(self._rect, self.columns, self.rows, self.areas)
        self.borders = bs
        if self.areas:
            self.keyed = cg
            self.cells = None
        else:
            self.cells = cg
            self.keyed = None
        
    def __getitem__(self, key):
        if self.cells:
            if isinstance(key, int):
                return self.cells[key]
            else:
                raise Exception("Must query cell-grid with indices")
        elif self.keyed:
            if isinstance(key, str):
                return self.keyed[key]
            else:
                print(">>>>>>>>>>", self, key)
                raise Exception("Must query area-grid with strings")

    def calc_grid(self, r, columns, rows, areas):
        cs = parse_line(r.w, columns)
        rs = parse_line(r.h, rows)
        if areas:
            areas = [a.strip().split(" ") for a in areas.split("/")]
        _grid = []
        keyed = {}
        borders = []
        for idx, rr in enumerate(r.subdivide(rs[:-1], "mxy", forcePixel=self.force_pixel)):
            cells = rr.subdivide(cs[:-1], "mnx", forcePixel=self.force_pixel)
            _grid.extend(cells)
            if areas:
                _keyed = {}
                last_area = None
                jdx = 0
                if idx >= len(areas):
                    continue
                for ra in areas[idx]:
                    if not ra:
                        continue
                    if ra == "||":
                        borders.append([last_area, Edge.MaxX, 1])
                        continue
                    elif ra == "|":
                        borders.append([last_area, Edge.MaxX, 0])
                        continue
                    elif ra == "__":
                        borders.append([rr, Edge.MinY, 1])
                        continue
                    elif ra == "_":
                        borders.append([rr, Edge.MinY, 0])
                        continue

                    _ra = ra.replace("_", "")
                    if ra.startswith("__"):
                        borders.append([_ra, Edge.MaxY, 1])
                    elif ra.startswith("_"):
                        borders.append([_ra, Edge.MaxY, 0])
                    elif ra.endswith("__"):
                        borders.append([_ra, Edge.MinY, 1])
                    elif ra.endswith("_"):
                        borders.append([_ra, Edge.MinY, 0])
                    
                    ra = _ra
                    if last_area and last_area == ra:
                        _keyed[ra] = _keyed[ra] = union_rect(_keyed[ra], cells[jdx])
                    else:
                        try:
                            _keyed[ra] = cells[jdx]
                        except IndexError:
                            print("-------------------")
                            print(self.columns)
                            print(self.rows)
                            print(self.areas)
                            print(ra)
                            raise Exception("Invalid")
                    last_area = ra
                    jdx += 1
                for k, v in _keyed.items():
                    if k not in keyed:
                        keyed[k] = v
                    else:
                        keyed[k] = union_rect(keyed[k], v)
        if areas:
            if borders:
                b = []
                for a, edge, weight in borders:
                    if isinstance(a, Rect):
                        b.append([a, edge, weight])
                    else: 
                        b.append([keyed[a], edge, weight])
            else:
                b = []

            if True:
                for k, v in keyed.items():
                    x, y, w, h = v
                    if self.warn_float:
                        if (not float(x).is_integer()
                            or not float(y).is_integer()
                            or not float(w).is_integer()
                            or not float(h).is_integer()):
                            print(">>> FLOAT RECT:::", k, v, "///", r)
            return keyed, b
        else:
            return _grid, []