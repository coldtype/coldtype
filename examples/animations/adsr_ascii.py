from coldtype import *

at = AsciiTimeline(1, 30, """
                           <
T           T           T
""")

@animation((1080, 1080), timeline=at, bg=0)
def choreography(f):
    v = at.ki("T").adsr([8, 110])

    return (StSt("T", Font.MutatorSans(), 500
        , wght=v)
        .align(f.a.r)
        .f(1))