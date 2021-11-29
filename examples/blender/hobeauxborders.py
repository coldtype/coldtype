from coldtype import *
from coldtype.blender import *

fnt = Font.Find("Hobeaux-Roc.*Bor")
styles = [
    "Aa ", "B  ", "Cc3", "Dd4", "Ee5",
    "Ff6", "Gg ", "Hh8", "Ii9", "Jj0",
    "Kk!", "Ll@", "Mm#", "Nn$", "Oo%",
    "Pp^", "Qq&", "Rr ", "Ss(", "Tt)",
    "Uu-", "Vv=", "Ww_", "Xx+", "Yy ",
]

def hobeauxBorder(r, style=0, fs=200):
    s = styles[style]
    b, c, m = [StSt(x, fnt, fs).pen() for x in s]
    bw, cw = [e.ambit().w for e in (b, c)]
    
    nh, nv = int(r.w/bw/2), int(r.h/bw/2)
    bx = Rect(bw*nh*2+cw*2, bw*nv*2).align(r)

    return PS([
        (b.layer(nh)
            .append(c)
            .distribute()
            .append(m)
            .mirrorx()
            .translate(*bx.pn)
            .mirrory(bx.pc)),
        (b.layer(nv)
            .distribute()
            .append(m)
            .rotate(90, "SW")
            .translate(cw, 0)
            .mirrory()
            .translate(*bx.pw)
            .mirrorx(bx.pc))])


@b3d_animation(timeline=len(styles))
def b1(f):
    return (hobeauxBorder(f.a.r.inset(150), f.i, 500)
        .pen()
        .f(hsl(0.7))
        .tag("border")
        | b3d(lambda bp: bp
            .extrude(0.25)
            , dn=True))