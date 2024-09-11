from coldtype import *
from coldtype.web.site import *

font = "PolymathVar"

header: jinja_html = """
"""
index: jinja_html = """
<!--<p id="fontName">{{ fonts[0].fonts[0].woff2_relative }}</p>-->
<p><span id="svgResult"></span></p>
"""
footer: jinja_html = """
"""

style: css = """
* { box-sizing: border-box; }
body { text-align: center; background: black; }
h1 { font-variation-settings: "wght" 900; }
h2 { font-variation-settings: "wght" 700; }
header a { color: royalblue; }
header a.current { color: hotpink; }
main { margin: 20px; }
"""

info = dict(
    title="Coldtype/p5js Experiment",
    description="An experiment",
    style=style,
    #script=script,
    font_name=font,
    scripts=[
        "https://unpkg.com/canvaskit-wasm@0.19.0/bin/canvaskit.js",
        #"https://cdn.rawgit.com/nodebox/g.js/master/dist/g.min.js",
        "https://cdn.jsdelivr.net/gh/generative-design/Code-Package-p5.js@master/libraries/gg-dep-bundle/gg-dep-bundle.js",
        "https://cdnjs.cloudflare.com/ajax/libs/opentype.js/0.7.3/opentype.min.js",
        "assets/hbjs.js",
        "assets/p5.min.js",
        "assets/script.js",
    ],
    templates=dict(_header=header, _footer=footer, index=index),
)

@site(ººsiblingºº(".")
      , port=8008
      , info=info
      , fonts={
        "text-font": dict(regular=font, _features=dict(ss01=True,ss02=True))
      })
def website(_):
    website.build()

def release(_):
    website.upload("example.com", "us-west-1", "personal")