from coldtype import *

@renderable(bg=1)
def shapes(r:Rect):
    s = Scaffold(r).numeric_grid(10, 10)
    return (P(
        s.view(),
        P(s["5|4*3|2"]).f(bw(0, 0.5)),
        P(s["4|3*3|2"]).f(bw(0, 0.25)),
        P(s["0|-1*3|-3"]).f(hsl(0.75, a=0.5)),
        P(s["-1|-2*-3|-3"]).f(hsl(0.75, a=0.5)),
        P(s["3|1*2|2"]).f(hsl(0.3, a=0.5)),
        P(s["-1|0*-2|2"]).f(hsl(0.3, a=0.5)),
        ))
