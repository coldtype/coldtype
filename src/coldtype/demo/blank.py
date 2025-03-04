from coldtype import *

co = Font.Cacheable(__sibling__("ColdtypeObviously-VF.ttf"))
mu = Font.Cacheable(__sibling__("MutatorSans.ttf"))

@renderable((500, 500), bg=hsl(0.75, 1, 0.7))
def render(r):
    circle = (P().oval(r.inset(70)).reverse())
    return P(
        (StSt("No renderables found in source file ... ".upper(),
            mu, 50, wdth=0.19, wght=0.5)
            .f(0, 0.5)
            .distribute_on_path(circle.rotate(-150))),
        (StSt("COLD\nTYPE",
            co, 130, r=1, wdth=0.5, tu=50)
            .f(hsl(0.07, 1, 0.8))
            .align(r)))