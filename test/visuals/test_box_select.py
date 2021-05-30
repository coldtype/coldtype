from coldtype.test import *

@test((1000, 1000), rstate=1)
def test_rect(r, rs):
    out = DATPens()
    out += (DATPen()
        .oval(r.inset(50))
        .f(0.8))
    
    if box := rs.shape_selection():
        if rs.mouse_down:
            box.f(None).s(hsl(0.6, s=1)).sw(5)
        else:
            box.f(hsl(0.7, a=0.2))
        out += box
    return out

polygons = [] # in-process save-cache

@test((1000, 1000), rstate=1, solo=1)
def test_polygon(r, rs):
    out = DATPens()
    oval = (DATPen()
        .oval(r.inset(150))
        .f(None)
        .s(0, 0.5)
        .sw(5))
    
    out += oval

    for p in polygons:
        out += p.copy().f(hsl(0.9, s=1, a=0.3))

    if mh := rs.mouse_history:
        saved, polygon = rs.polygon_selection()
        inter = (polygon.copy()
            .intersection(oval).f(hsl(0.3, s=1, a=0.3)).s(None))
        out += inter
        if saved:
            polygons.append(inter.copy())
        else:
            out += polygon.copy().f(hsl(0.5, s=1, a=0.1))
    
    return out