from coldtype import *
from coldtype.webserver.cdelopty import evalcdel

fonts = {
    "mistral": Font.Cacheable("~/Type/fonts/fonts/_script/MistralD.otf"),
    "co": Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")}

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

@renderable()
def stub(r):
    return evalcdel(test, r, fonts)