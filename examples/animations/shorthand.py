from coldtype import *

@animation(timeline=600)
def shorthand(f):
    return (DP()
        .define(r=f.a.r.take(150, "mdx").square())
        .gs("$r← ↖|c:=355|$r↑ ↗|c|$r→ ↘|c|$r↓ ↙|c|§")
        .f(None).s(0).sw(1)
        #.rotate(f.e("l", 1, 0)*360)
        )
