from coldtype import *
from coldtype.web.site import *

header: jinja_html = """
<h1>header</h1>
{{ nav_html|safe }}
"""
index: jinja_html = """
<p>index page</p>
"""
about: jinja_html = """
<p>about page</p>
"""
footer: jinja_html = """
<h2>footer</h2>
"""

style: css = """
* { box-sizing: border-box; }
body { text-align: center; }
h1 { font-variation-settings: "wght" 900; }
h2 { font-variation-settings: "wght" 700; }
header a { color: royalblue; }
header a.current { color: hotpink; }
main { border: 1px solid black; margin: 20px; }
"""

script: js = """
console.log("hello world")
"""

info = dict(
    title="Skeleton",
    description="This is empty code to copy",
    style=style,
    script=script,
    templates=dict(_header=header, _footer=footer, index=index, about=about),
    navigation={"Home": "/", "About": "/about"},
)

@site(ººsiblingºº(".")
      , port=8008
      , info=info
      , fonts={
        "text-font": dict(regular="Cheee_Caption", _embed=True)
      })
def website(_):
    website.build()

def release(_):
    website.upload("example.com", "us-west-1", "personal")