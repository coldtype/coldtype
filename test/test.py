from test_preamble import *

from coldtype import StyledString
from coldtype.utils import pen_to_svg
from furniture.geometry import Rect
from random import randint

try:
    os.makedirs(dirname + "/artifacts")
except FileExistsError:
    pass

def save_svg_artifact(filename, recording, dimensions):
    svg_pen = flipped_svg_pen(recording, dimensions[1])
    d = svg_pen.getCommands()
    svg = f"""
    <svg width="{dimensions[0]}" height="{dimensions[1]}" xmlns="http://www.w3.org/2000/svg">
        <path d="{d}"/>
    </svg>
    """
    with open(dirname + "/artifacts/" + filename, "w") as f:
        f.write(svg)

f = "~/Library/Fonts/Nostrav0.9-Stream.otf"
f = "~/Library/Fonts/HobeauxRegular.otf"
f = "~/Library/Fonts/FormaDJRTextItalic.otf"

dimensions = (1000, 1000)
ss = StyledString(f"Hallo {randint(0, 9)} Welt",
    fontFile="~/Type/fonts/fonts/ObviouslyVariable.ttf",
    fontSize=300,
    tracking=0,
    features=dict(ss01=True, ss05=True, ss06=True),
    variations=(dict(wght=1, slnt=1, wdth=1, scale=True)))
    
ss.place(Rect((0, 0, *dimensions)))
save_artifact("obviously.svg", pen_to_svg(ss.asRecording(), dimensions))