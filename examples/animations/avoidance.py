from coldtype import *
import numpy as np

# after https://editor.p5js.org/creativecoding/sketches/ncNWaEkTw

minMouseDist = 20000
words = """
Just getting
out of the
way
"""

# https://stackoverflow.com/questions/21030391/how-to-normalize-a-numpy-array-to-a-unit-vector

def normalized(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / np.expand_dims(l2, axis)

def displacer(r, c):
    txt = (StSt(words, "Times", 100)
        .lead(20)
        .align(r)
        .collapse())
    
    for g in txt:
        p = g.ambit(tx=1, ty=1).psw
        mouseDist = Line(p, c).length()
        p2 = np.array([p.x - c.x, p.y - c.y])
        distDifference = minMouseDist - mouseDist
        
        p2x, p2y = (normalized(p2) * math.sqrt(distDifference))[0]
        g.t(p2x, p2y)

    return P(
        P().oval(Rect.FromCenter(c, 50)).f(1),
        txt.f(1))

#@ui(bg=0)
def avoid_ui(u):
    return displacer(u.r, u.c)

@animation(tl=Timeline(500, 30), bg=0, render_bg=1)
def avoid_anim(f):
    o = P().oval(f.a.r.take(f.e("eeio", 7, r=(900, 100)), "CX").square())
    c, _ = o.point_t(f.e("seio", 3))
    return displacer(f.a.r, c)