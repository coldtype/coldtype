import ast, inspect

from coldtype import *
from coldtype.webserver.cdelopty import evalcdel

fonts = {
    "mistral": Font.Cacheable("~/Type/fonts/fonts/_script/MistralD.otf"),
    "co": Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")}

@renderable(Rect(1080, 1080))
def scratch(r):
    return DATPens([
        (DATPen(r).f(0)),
        (DATPen().oval(r.inset(50))
            .f(hsl(0.6, s=1))
            .align(r)),
        (StSt("Cold!", "co", 500,
            wdth=0.25, wght=1, tu=-80, r=1, ro=1)
            .fit(r.w)
            .pens()
            .align(r)
            .f(1)
            .understroke(0, 30))])

#src = inspect.getsource(scratch.func).split("\n")[1:]
#tree = ast.parse("\n".join(src))
#print(tree.[0])
#for f, v in ast.iter_fields(tree):
#    print(f, v)
#for n in ast.iter_child_nodes(tree):
#    for nn in ast.iter_child_nodes(n):
#        print(nn)

test = [
    ["P", "®", ".", ["f", 0]],
    ["P", ".",
        ["oval", ["R", "®", ".", ["inset", 50]]],
        ["f", ["hsl", 0.6, {"s":1}]],
        ["align", "®"]],
    ["S", "Cold!", "co", 500,
        {"wdth":0.25, "wght":1, "tu":-80, "r":1, "ro": 1},
        ".",
        ["fit", "®", ".w"],
        ["pens"],
        ["align", "®"],
        ["f", 1],
        ["understroke", 0, 30]]]

@renderable(solo=1)
def stub(r):
    return evalcdel(test, r, fonts)