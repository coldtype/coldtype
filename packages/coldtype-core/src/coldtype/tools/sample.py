from coldtype import *
from coldtype.tool import Tool

tool = Tool(ººinputsºº, dict(
    font=[Font.MutatorSans(), str, None, "Font search string"],
    text=["Sample", str, None, "Text to animate"],
    axis=[None, str, None, "Axis to animate"]))

text = tool.state["text"]

font:Font = tool.state["font"]
fontSize = tool.state["fontSize"]

axis = tool.state.get("axis")
if axis is None and font.axes:
    axis = font.axes[0]

@animation((1080, 1080), tl=Timeline(30, 24), bg=0)
def view(f):
    return (StSt(text, font, fontSize, variations={**tool.state["fontVariations"], **{axis:f.e("ceo", 1)}})
        .align(f.a.r)
        .f(1)
        .scaleToRect(f.a.r.inset(60)))