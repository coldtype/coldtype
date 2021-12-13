from coldtype import *
from coldtype.css import *

at = AsciiTimeline(1, """
                                        <
            ~i                   ~o
A        A      B            B
""", keyframes={
    "A": dict(fontSize=50),
    "B": dict(fontSize=670),
}, eases={
    "i": cubicBezier(0.25,0.1,0.25,1.5),
    "o": "qeio"
})

@animation(tl=at, bg=0)
def css1(f):
    return [
        (StSt("OK", Font.MutatorSans()
            , **{
                **f.t.kf(),
                **f.t.kf(
                    keyframes=dict(A=dict(wght=1), B=dict(wght=0)),
                    eases=dict(i="eeo", o="eeio")),
                **f.t.kf(
                    keyframes=dict(A=dict(wdth=1), B=dict(wdth=0)),
                    eases=dict(i="eeo", o="ceio")
                )})
            .align(f.a.r)
            .f(1))]