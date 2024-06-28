from coldtype import *
from coldtype.web.site import *

header: jinja_html = """
<div class="wrapper">
    <h1>Coldtype</h1>
    <ul class="link-list">{% for k,v in info["externals"].items() %}
        <li><a href="{{v}}">{{k}}</a></li>
    {% endfor %}</ul>
</div>
"""
index: jinja_html = """
<p><em>Coldtype makes tools for advanced typography (and some other related stuff).</em></p>
<hr/>
<p>Currently those tools include:</p>
<ul>
    <li><a href="">coldtype</a>: an open-source <strong>Python library</strong> for programming animated display typography</li>
    <li><a href="">ST2</a>: an open-source <strong>Blender add-on</strong> for doing good typography in 3D</li>
    <li><a href="">b3denv</a>: an open-source command-line utility for working with Blender and its embedded Python</li>
</ul>
<hr/>
<p>Here are some talks about Coldtype & ST2:</p>
<ul>
    <li><a href="https://vimeo.com/864468653">“A Font is a Percussion Instrument”</a> (Typographics 2023)</li>
    <li><a href="https://youtu.be/gV2laWd727U">The How & Why of ST2</a> (inScript 2022)</li>
</ul>
"""
footer: jinja_html = """
<p>Coldtype is a project of <a href="https://goodhertz.com">Goodhertz</a>;<br/>development is led by <a href="https://robstenson.com">Rob Stenson</a>.</p>
"""

style: css = """
* {
    box-sizing: border-box;
}
:root {
    --border-color: #eee;
}
html, body {
    height: 100%;
}
body {
    /* background: hsl(130, 70%, 93%); */
    background: white;
    color: black;
    font-family: var(--text-font);
    text-align: center;
    display: flex;
    flex-direction: column;
}
em {
    font-style: normal;
    font-variation-settings: "ital" 1;
}
a {
    color: royalblue;
    text-decoration: none;
}

header { border-bottom: 1px solid var(--border-color); }
footer { border-top: 1px solid var(--border-color); }

header, footer {
    flex: 1;
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    max-height: 300px;
    min-height: 200px;
}
.link-list {
    list-style: none;
    display: flex;
    flex-wrap: wrap;
    margin-top: 16px;
    justify-content: center;
    row-gap: 12px;

}
.link-list li {
    /* display: flex; */
}
.link-list li:not(:last-child)::after {
    content: "///";
    color: #ccc;
}
.link-list li a {
    padding: 4px 7px;
    background: whitesmoke;
}
.link-list li a:hover {
    background: lightpink;
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
    padding: 20px;
    margin: auto auto;
}
main p { margin-bottom: 16px; }
main hr {
    border: none;
    border-top: 2px solid #eee;
    margin-bottom: 20px;
    margin: 26px 60px 30px;
}
main strong { font-variation-settings: "wght" 700; }
main ul {
    margin-left: 20px;
}
main li {
    margin-bottom: 10px;
}
main li a {
    font-variation-settings: "wght" 800;
}
h1 {
    font-variation-settings: "wght" 900;
}
"""

script: js = """
// window.addEventListener("mousemove", function(event) {
//   console.log("mousemouse");
// });
"""

info = dict(
    title="Coldtype",
    description="Coldtype is a programming library for advanced typography (and other stuff)",
    style=style,
    script=script,
    templates=dict(_header=header, _footer=footer, index=index),
    externals={
        "github": "https://github.com/coldtype",
        "youtube": "https://www.youtube.com/channel/UCIRaiGAVFaM-pSErJG1UZFA",
        "tutorials": "https://coldtype.goodhertz.com/",
        "q&a forum": "https://github.com/goodhertz/coldtype/discussions",
    },
)


@site(ººsiblingºº(".")
      , port=8008
      , livereload=True
      , info=info
      , fonts={"text-font": dict(regular="MDIO-VF")})
def site(_):
    return None


def release(_):
    site.upload("coldtype.xyz", "us-west-1", "personal")