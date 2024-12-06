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

    s["b"].grid(4, 4)
    s["c"].numeric_grid(5)

    return P(
        s.view(fontSize=18, fill=False),
        s["a"].cssborders(lambda p: p.fssw(-1, hsl(0.7), 5), -1),
        s["a/d"].cssborders(),
        s["d"].cssborders(),
        s["a"].cssborders(-1, bold),
        s.cssborders(reg, bold),
        s["b"].borders().fssw(-1, hsl(0.07, 0.7), 2),
        s["c"].borders().fssw(-1, hsl(0.7), 1))