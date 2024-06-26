from coldtype import *
from coldtype.web.site import *
from coldtype.web.fonts import woff2s
from sourcetypes import jinja_html, css, js

header: jinja_html = """
<h1>Coldtype</h1>
"""
index: jinja_html = """
<div class="wrapper">
    <p><em>Coldtype makes tools for advanced typography and graphics programming</em></p>
    <p>Currently those tools include:</p>
    <ul>
        <li><a href="">coldtype</a>: an open-source <strong>Python library</strong> for programming animated display typography</li>
        <li><a href="">ST2</a>: an open-source <strong>Blender add-on</strong> for doing good typography in 3D</li>
        <li><a href="">b3denv</a>: an open-source command-line utility for working with Blender and its embedded Python</li>
    </ul>
</div>
"""
footer: jinja_html = """
<h3>Footer</h3>
"""

style: css = """
* {
    box-sizing: border-box;
}
html, body {
    height: 100%;
}
body {
    background: hsl(130, 70%, 93%);
    color: black;
    font-family: var(--text-font);
    text-align: center;
    display: flex;
    flex-direction: column;
}
header { border-bottom: 10px solid white; }
footer { border-top: 10px solid white; }
header, footer {
    height: 100px;
    line-height: 100px;
}
main {
    flex: 1;
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
}
main .wrapper {
    text-align: left;
    max-width: 600px;
    margin: auto auto;
}
main p {
    margin-bottom: 10px;
}
main strong {
    font-weight: bold;
}
"""

script: js = """
window.addEventListener("mousemove", function(event) {
  console.log("mousemouse");
});
"""

info = dict(
    title="Coldtype",
    description="Coldtype is a programming library for advanced typography (and other stuff)",
    style=style,
    script=script,
    templates=dict(_header=header, _footer=footer, index=index),
    fonts=woff2s(
        ººsiblingºº("./assets/fonts"),
        {"text-font": dict(
            regular="MDIO0.6-Regular",
            regularitalic="MDIO0.6-Italic",
            bold="MDIO0.6-Bold",
        )},
    ),
)


@site(ººsiblingºº(".")
      , port=8008
      , multiport=8009
      , info=info)
def coldtypexyz(_):
    return None