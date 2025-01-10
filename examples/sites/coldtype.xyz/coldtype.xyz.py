from coldtype import *
from coldtype.web.site import *

header: jinja_html = """
<div class="wrapper">
    <h1 style="max-width:400px"><img alt="Coldtype" style="width:100%" src="/media/coldtype_wavey.jpg"/></h1>
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
    <li><a href="https://github.com/coldtype/coldtype">coldtype</a>: an open-source <strong>Python library</strong> for programming animated display typography</li>
    <li><a href="https://coldtype.xyz/st2">ST2</a>: an open-source <strong>Blender add-on</strong> for doing good typography in 3D</li>
    <li><a href="https://github.com/coldtype/b3denv">b3denv</a>: an open-source command-line utility for working with Blender and its embedded Python</li>
    <li><a href="https://github.com/stenson/nudge">Nudge</a>: a VS Code extension that allows keyboard shortcuts to increment/decrement numeric values (and letters) and then immediately save the file</li>
</ul>
<hr/>
<p>
If you’re looking to take a class on Coldtype, <a href="https://coopertype.org/events/type-sound-code-an-introduction-to-coldtype">here’s one</a> that’s about to start in February.
</p>
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
* { box-sizing: border-box; }
:root { --border-color: #ddd; }
html, body { height: 100%; }
body {
    background: white;
    color: #222;
    font-family: var(--text-font);
    display: flex;
    flex-direction: column;
}
em { font-style: normal; --text-font: fvs(ital=1); }
a { color: royalblue; text-decoration: none; }
h1 { --text-font: fvs(wght=1); }

header, footer { background: white; }
header { border-bottom: 1px solid var(--border-color); }
footer { border-top: 1px solid var(--border-color); }

header, footer, main {
    flex: 1;
    padding: 30px 20px;
    display: flex;
    justify-content: center;
    align-items: center;
}
header, footer {
    text-align: center;
    max-height: 200px;
    min-height: 200px;
}
main {
    padding: 50px 20px;
}
.wrapper { max-width: 500px; }

.link-list {
    list-style: none;
    display: flex;
    flex-wrap: wrap;
    margin-top: 6px;
    justify-content: center;
    row-gap: 12px;
}
.link-list li:not(:last-child)::after { content: "///"; color: #ccc; }
.link-list li a { padding: 4px 7px; background: whitesmoke; }
.link-list li a:hover { background: lightpink; }

main p { margin-bottom: 16px; }
main strong { --text-font: fvs(wght=0.7); }
main hr {
    border: none;
    border-top: 2px solid #eee;
    margin-bottom: 20px;
    margin: 26px 60px 30px;
}
main ul { margin-left: 20px; }
main li { margin-bottom: 10px; }
main li a { --text-font: fvs(wght=0.75); }
"""

info = dict(
    title="Coldtype",
    description="Coldtype is a programming library for advanced typography (and other stuff)",
    style=style,
    templates=dict(_header=header, _footer=footer, index=index),
    externals={
        "github": "https://github.com/coldtype",
        "youtube": "https://www.youtube.com/channel/UCIRaiGAVFaM-pSErJG1UZFA",
        "tutorials": "https://coldtype.goodhertz.com/",
        # "q&a forum": "https://github.com/goodhertz/coldtype/discussions",
    },
)

@renderable(preview_scale=0.25)
def favicon(r):
    return StSt("C", Font.ColdObvi(), 1300, wdth=1).align(r).f(0)

@site(ººsiblingºº(".")
      , port=8008
      , livereload=True
      , info=info
      , favicon=favicon
      , fonts={"text-font": dict(regular="MDIO-VF")})
def website(_):
    website.build()

@renderable((1080, 200), fmt="png")
def logo(r):
    return (Glyphwise("COLDTYPE", lambda g: Style(Font.ColdObvi(), 200, wdth=ez(g.e, "l", 1, rng=(1, 0))))
        .f(0)
        .align(r))

def release(_):
    website.upload("coldtype.xyz", "us-west-1", "personal")