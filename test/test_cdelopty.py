from coldtype import *
from coldtype.webserver.cdelopty import evalcdel

test = [
    ["P", ".",
        ["oval", ["R", "®", ".", ["inset", 50]]],
        ["f", ["hsl", 0.6, {"s":1, "a":0.5}]],
        ["align", "®"]
    ],
    ["S", "COLD", "-", 500,
        {"wdth":0.5, "tu":-80, "r":1, "ro": 1},
        ".",
        ["pens"],
        ["align", "®"],
        ["f", 1],
        ["understroke", 0, 30],
        ["rotate", -15]]
]

@renderable()
def stub(r):
    return evalcdel(test)