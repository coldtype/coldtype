from coldtype import *

@renderable((500, 500))
def borders(r):
    s = Scaffold(r)
    s.cssgrid("a a", "a a", "a | b __/ c | d",
        a=("a a", "a a", "a_ || b / c || d"))
    
    s["d"].cssgrid("a a", "a a", "a | b _/ c d")
    s["a/d"].cssgrid("a a", "a a", "a b _/ c | d")

    reg = lambda p: p.fssw(-1, hsl(0.5), 10)
    bold = lambda p: p.fssw(-1, hsl(0.9), 20)

    return P(
        s["a"].borders(lambda p: p.fssw(-1, hsl(0.7), 5), -1),
        s["a/d"].borders(),
        s["d"].borders(),
        s["a"].borders(-1, bold),
        s.borders(reg, bold))