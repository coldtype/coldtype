from coldtype import *
from coldtype.raster import *

fonts = [f for f in Font.List(r".*", r"_wood|_historical") if "Catchwords" not in f.name and "cmu" not in f.name and "AmericanStars" not in f.name and "BordersOne" not in f.name and "BookJacketAlts" not in f.name]

@animation((1080, 1080/3), bg=0, tl=Timeline(60, 12))
def options(f):
    rsi = random_series(0, len(fonts), f.i, 10000, mod=int)

    p = P()
    txt = "HELLO"
    idx = 0
    last = None
    total_width = 0
    for c in txt:
        while True:
            #print(idx)
            fnt = fonts[rsi[idx]]
            if fnt == last:
                idx += 1
                continue
            last = fnt
            idx += 1
            try:
                candidate = StSt(c, fnt, 200)[0]
                idx += 1
                if "notdef" in candidate.data("glyphName"):
                    #print("! notdef")
                    pass
                else:
                    candidate.scaleToRect(f.a.r.take(200, "CY")).zero(tx=1, ty=1).unframe()
                    w = candidate.ambit(tx=1).w
                    if idx < 5000 and (total_width + w) > 900:
                        #print("! too wide")
                        continue
                    total_width += w
                    #print(">", c, candidate.data("glyphName"), fnt.name)
                    p.append(candidate)
                    break
            except:
                pass

    return (p
        #.mapv(lambda p: p.up().insert(0, P(p.ambit(tx=0, ty=0)).f(hsl(0.3, a=0.3))).zero())
        #.mapv(λ.zero(tx=1, ty=1).unframe())
        .spread(10, tx=1, zero=1)
        .align(f.a.r)
        .f(0)
        .f(1).ch(phototype(f.a.r, 2, 80, 30, 1))
        )

@animation(tl=Timeline(60, 12), bg=0, solo=1)
def three(f):
    return (P(
        options.pass_img(f.i).in_pen().ch(luma(f.a.r)).ch(precompose(f.a.r)).ch(fill(hsl(0.6, 0.7))),
        options.pass_img(f.i+10).align(f.a.r, "C").in_pen().ch(luma(f.a.r)).ch(precompose(f.a.r)).ch(fill(hsl(0.40, 0.65))),
        options.pass_img(f.i+20).align(f.a.r, "N").in_pen().ch(luma(f.a.r)).ch(precompose(f.a.r)).ch(fill(hsl(0.90, 0.7)))
    ))