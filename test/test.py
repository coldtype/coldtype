import os
import sys
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.realpath(dirname + "/.."))

from coldtype import StyledString, flipped_svg_pen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import replayRecording
from furniture.geometry import Rect

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
ss = StyledString("Sello Furled",
    fontFile="~/Type/fonts/fonts/ObviouslyVariable.ttf",
    fontSize=300,
    tracking=0,
    features=dict(ss01=True),
    variations=(dict(wght=1, slnt=1, wdth=1, scale=True)))
ss.place(Rect((0, 0, *dimensions)))
save_svg_artifact("obviously.svg", ss.asRecording(), dimensions)