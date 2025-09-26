from coldtype import *
from coldtype.raster import *
from functools import partial
from random import Random

fnt = Font.Find("MontreuilPlay")

import numpy as np
import random

txt = "CLAWHAMMER"

options = [
    [1, 2],
    [1, 2, 3, 4, 5],
    [3, 4, 5],
    [3, 4, 5, 2],
    [3, 4, 5],
    [3, 4, 5, 6],
    [3, 4, 5],
    [3, 4, 5],
    [3, 4, 5],
    [3, 4, 5, 6, 7],
    [6, 7]
]

repeats = len(options)

def generate_matrix_sequence(changes_per_step):
    np.random.seed(1)
    random.seed(1)
    
    current_matrix = np.random.randint(1, 3, size=(repeats, len(txt)))

    for idx, x in enumerate(current_matrix):
        for jdx, _ in enumerate(x):
            choices = options[idx]
            weights = np.array([0.01] + [0.95/(len(choices)-1)] * (len(choices)-1))
            current_matrix[idx, jdx] = random.choices(options[idx], weights=weights)[0]
            #if random.random() < 0.05:
            #    current_matrix[idx, jdx] = 4

    unvisited = set((i, j) for i in range(repeats) for j in range(len(txt)))
    matrices = [current_matrix.copy()]
    
    while unvisited:
        num_changes = min(changes_per_step, len(unvisited))
        cells_to_change = random.sample(list(unvisited), num_changes)
        new_matrix = current_matrix.copy()
        
        for i, j in cells_to_change:
            choices = options[i]
            weights = np.array([0.01] + [0.95/(len(choices)-1)] * (len(choices)-1))
            current_val = current_matrix[i, j]
            new_val = random.choice([x for x in choices if x != current_val])
            if random.random() < 0.01:
                new_val = 0
            new_matrix[i, j] = new_val
            unvisited.remove((i, j))
        
        matrices.append(new_matrix)
        current_matrix = new_matrix
    
    return matrices


matrices = generate_matrix_sequence(2)
matrices.append(matrices[-1].copy())
matrices.append(matrices[-1].copy())
matrices.append(matrices[-1].copy())
matrices.append(matrices[-1].copy())
matrices.insert(0, matrices[0].copy())
matrices.insert(0, matrices[0].copy())
matrices.insert(0, matrices[0].copy())

@animation(bg=0, tl=Timeline(len(matrices)*2, 24))
def scratch(f:Frame):
    _r = Rect(1000)
    io = P().m(_r.psw).l(_r.pse.o(-400, 0)).ioc(_r.pne.o(-100, 0), 0).l(_r.pne).fssw(-1, 1, 2)
    #return io

    def mp(line):
        def character(x):
            style = matrices[int(f.e("l", 1, (0, len(matrices)-1)))][line.i][x.i]
            return (StSt(x.el, fnt, 100, features={f"ss0{style}":1}))

        return P().enumerate(txt, character).spread(0)
    
    #_mp = partial(mp, 100, "GOODHERTZ")
    return (P(
        # _mp(0, [0, 1, 2]),
        # _mp(1, [5, 3, 4]),
        # _mp(2, [5, 3, 4]),
        # #_mp([6]),
        # _mp(7, [0, 3, 4, 5]),
        # #_mp([0]),
        # _mp(8, [0, 3, 4]),
        # _mp(10, [0, 3, 4]),
        # _mp(11, [0, 3, 4]),
        # #_mp([3, 4]),
        # #_mp([3, 4]),
        # _mp(9, [0, 3, 4, 5]),
        # #_mp([3, 4, 5]),
        # _mp(3, [6, 7]),
    )
    .enumerate(range(0, repeats), mp)
    #.f(hsl(0.3, 0.90, 0.70))
    #.map(lambda p: p.insert(0, P(p.ambit(tx=0, ty=0)).f(hsl(0.70, 0.90, 0.70))))
    #.index(2, lambda p: p.t(-10, 0))
    #.stack(f.e(io, 1, (18, 22)), ty=0)
    .stack(18, ty=0)
    .align(f.a.r, tx=0, ty=0)
    .collapse()
    #.pen().ro().fssw(-1, 1, 4)
    .f(1)
    #.fssw(-1, 1, 1)
    .scale(0.9)
    .ch(phototype(f.a.r, 1.5 , 150, 50))
    )

release = scratch.gifski(open=True)