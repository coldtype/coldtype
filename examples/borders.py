from coldtype import *

@renderable((500, 500))
def borders(r):
    m = Mondrian(r)
    m.cssgrid("a a", "a a", "a | b __/ c | d",
        a=("a a", "a a", "a_ || b / c || d"))
    
    m["d"].cssgrid("a a", "a a", "a | b _/ c d")
    m["a/d"].cssgrid("a a", "a a", "a b _/ c | d")

    reg = lambda p: p.fssw(-1, hsl(0.5), 10)
    bold = lambda p: p.fssw(-1, hsl(0.9), 20)

    return P(
        m["a"].borders(lambda p: p.fssw(-1, hsl(0.7), 5), -1),
        m["a/d"].borders(),
        m["d"].borders(),
        m["a"].borders(-1, bold),
        m.borders(reg, bold))