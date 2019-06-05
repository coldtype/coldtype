import os
import sys
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.realpath(dirname + "/.."))

from coldtype import StyledString
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import replayRecording
from furniture.geometry import Rect

dimensions = (1000, 1000)
f = "~/Library/Fonts/Nostrav0.9-Stream.otf"
f = "~/Library/Fonts/HobeauxRegular.otf"
f = "~/Library/Fonts/FormaDJRTextItalic.otf"
f = "~/Type/fonts/fonts/ObviouslyVariable.ttf"
ss = StyledString("Hello World",
    fontFile=f,
    fontSize=300,
    tracking=0,
    features=dict(ss01=True),
    variations=(dict(wght=1, slnt=1, wdth=1, scale=True)))
ss.place(Rect((0, 0, *dimensions)))
svg_pen = SVGPathPen(None)
rp = ss.asRecording()

for idx, (t, pts) in enumerate(rp.value):
    rp.value[idx] = (t, [(x, dimensions[0]-y) for x, y in pts])

replayRecording(rp.value, svg_pen)
d = svg_pen.getCommands()

svg = f"""
<svg width="{dimensions[0]}" height="{dimensions[1]}" xmlns="http://www.w3.org/2000/svg">
  <path d="{d}"/>
</svg>
"""

with open(dirname + "/artifacts/test.svg", "w") as f:
    f.write(svg)