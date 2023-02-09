from coldtype import *
from coldtype.css import *

at = AsciiTimeline(1, """
                                            <
                ~i                   ~o
    A        A      B            B
    C     C            D        D
                ~x                   ~y
""", keyframes={
    "A": dict(fontSize=100),
    "B": dict(fontSize=250),
}, eases={
    "i": cubicBezier(0.25,0.1,0.25,3.5),
    "o": "qeio"
})

@animation(tl=at, bg=0)
def css1(f):
    return [
        (StSt("OK", Font.MutatorSans(), **{
            **f.t.kf(),
            **f.t.kf(
                keyframes=dict(C=dict(wght=0), D=dict(wght=1)),
                eases=dict(x="eeo", y="eeo")),
            **f.t.kf(
                keyframes=dict(A=dict(wdth=1), B=dict(wdth=0)),
                eases=dict(i="sei", o="eei"))})
            .align(f.a.r)
            .f(1))]