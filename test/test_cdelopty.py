from coldtype import *
from coldtype.webserver.cdelopty import evalcdel

f1 = Font.Cacheable("~/Type/fonts/fonts/_script/MistralD.otf")
fonts = {"mistral":f1}

test = [
    ["P", "®", ".", ["f", 0]],
    ["P", ".",
        ["oval", ["R", "®", ".", ["inset", 50]]],
        ["f", ["hsl", 0.6, {"s":1}]],
        ["align", "®"]],
    ["S", "Cold!", "mistral", 500,
        {"wdth":0.5, "tu":-80, "r":1, "ro": 1},
        ".",
        ["pens"],
        ["align", "®"],
        ["f", 1],
        ["understroke", 0, 30],
        ["rotate", -15]]]

@renderable()
def stub(r):
    return evalcdel(test, r, fonts)