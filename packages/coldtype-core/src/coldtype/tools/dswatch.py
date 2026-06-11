from coldtype import *
from coldtype.tool import *

tool = Tool(ººinputsºº, dict(
    font=[Font.MutatorSans(), str, None, "Font search string"],
    text=["A", str, None, "Text to animate"],
    easingCurve=["ceio", str, None, "Easing curve"],
    )
    , defaultFontSize=350
    , print_fonts=False
    , watch_fonts=True)

text = tool.state["text"]
fontCached:Font = tool.state["font"]
fontSize = tool.state["fontSize"]

font = Font(fontCached.path, cacheable=False)

@animation((1080, 1080), tl=Timeline(60, 30), bg=0, watch=[font])
def view(f):
    variations = {}
    for idx, (k, v) in enumerate(font.variations().items()):
        variations[k] = f.e(tool.state["easingCurve"], idx+1)

    return (StSt(text, font, fontSize, variations=variations)
        .align(f.a.r)
        .f(1))