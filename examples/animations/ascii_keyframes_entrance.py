from coldtype import *

at = AsciiTimeline(2, """
                                        <
N         W                    W
A         B         B          A
   ~i                    ~o
C           D     D            E
""")

@animation((1080, 540), tl=at, bg=0, release=lambda x: x.gifski())
def keyframes(f):
    def variate(x):
        fi = f.i - x.i
        wdth = at.kf(fi=fi
            , keyframes=dict(N=0, W=1)
            , eases=dict(i="eio", o="eei"))
        return Style(Font.ColdObvi(), 100, wdth=wdth)

    def animate(i, p):
        fi = f.i - i*1
        ty = at.kf(fi=fi
            , keyframes=dict(A=-360, B=0)
            , eases=dict(i="eeo", o="eeio"))
        r = at.kf(fi=fi
            , keyframes=dict(C=360, D=0, E=-360*2)
            , eases=dict(i="eeio", o="seio"))
        p.t(0, ty if i%2 != 0 else -ty).rotate(r)

    return (Glyphwise("COLDTYPE", variate)
        .align(f.a.r)
        .mapv(animate)
        .reverse()
        .fssw(1, 0, 9, 1))