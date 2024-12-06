from coldtype import *

@renderable()
def boxes(r):
    l = (Scaffold(r)
        .cssgrid(r"auto 30%", r"50% auto", "x y / z q", {
            "x": ("200 a", "a a", "a b / a c"),
            "x/c": ("a a", "a a", "g a / i a"),
            "q": ("a a", "a a", "q b / c d")
        }))

    return P(
        l.view(),
        StSt("X", Font.MuSan(), 200, wght=1).align(l["x"]),
        StSt("Y", Font.MuSan(), 200, wght=1).align(l["y"]),
        StSt("Z", Font.MuSan(), 200, wght=1).align(l["z"]),
        StSt("Q", Font.MuSan(), 200, wght=1).align(l["q"]),
        StSt("A", Font.RecMono(), 100).align(l["a"]).f(hsl(0.9)),
        StSt("B", Font.RecMono(), 100).align(l["b"]).f(hsl(0.9)),
        StSt("C", Font.RecMono(), 100).align(l["c"]).f(hsl(0.9)),
        StSt("G", "Comic Sans", 50).align(l["g"]).f(0),
        StSt("A", "Comic Sans", 50).align(l["x/c/a"]).f(0),
        StSt("I", "Comic Sans", 50).align(l["i"]).f(0),
        P().oval(l["x/c/a"]).fssw(-1, hsl(0.3, a=0.5), 10),
        StSt("Q/Q", "Comic Sans", 50).align(l["q/q"]).f(0),)

@renderable((1080, 540))
def boxes2(r):
    l = Scaffold(r).grid(2, 2)
    
    return P(
        l.view(),
        P().oval(l[0].rect.square().inset(10)).fssw(-1, hsl(0.9, 1), 2))

@renderable((1080, 540))
def boxes3(r):
    l = Scaffold(r).labeled_grid(5, 5)
    
    return P(
        l.view(),
        P().oval(l["d3"].rect.square().inset(10)).fssw(-1, hsl(0.9, 1), 2)
        )

@renderable((1080, 540), solo=1)
def boxes4(r):
    d = 15
    l = Scaffold(r.inset(4)).numeric_grid(d, d)
    
    def rectangular_rings(grid_width, grid_height):
        center_x, center_y = grid_width // 2, grid_height // 2
        max_radius = max(center_x, center_y)
        rings = []

        for r in range(max_radius + 1):
            ring = [
                f"{x}|{y}"
                for x in range(center_x - r, center_x + r + 1)
                for y in range(center_y - r, center_y + r + 1)
                if (
                    (x == center_x - r or x == center_x + r or y == center_y - r or y == center_y + r)
                    and 0 <= x < grid_width and 0 <= y < grid_height
                )
            ]
            if ring:
                rings.append(ring)
        return rings
    
    cells = (P().enumerate(l.cells(), lambda x: P(x.el.r.inset(2)).f(0).tag(x.el.tag())))
    
    for idx, ring in enumerate(rectangular_rings(d, d)):
        for tag in ring:
            cells.find_(tag).f(hsl(idx*0.25))

    return P(
        #l.view(),
        cells,
        #P().oval(l["d3"].rect.square().inset(10)).fssw(-1, hsl(0.9, 1), 2)
        )