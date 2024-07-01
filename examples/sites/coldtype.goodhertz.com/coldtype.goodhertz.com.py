from coldtype import *
from coldtype.web.site import *
from functools import partial

hierarchy = {
    "mains": ["introduction.html", "about.html", "overview.html", "install.html", "classes_functions.html"],
    "tutorials": ["tutorials/shapes.html", "tutorials/geometry.html", "tutorials/text.html", "tutorials/animation.html", "tutorials/drawbot.html", "tutorials/blender.html"],
    "cheatsheets": ["cheatsheets/viewer.html", "cheatsheets/easing.html", "cheatsheets/rectangles.html", "cheatsheets/oneletter.html", "cheatsheets/text.html"],
}

def section(section, site):
    return sorted([p for p in site.pages if p.slug in hierarchy[section]], key=lambda p: hierarchy[section].index(p.slug))

info = dict(
    title="Coldtype Tutorials",
    description="These are Coldtype tutorials",
    navigation={
        #"Home": "/",
        #"About": "/about"
        "coldtype.xyz": "https://coldtype.xyz/",
        "blog": "https://blog.coldtype.xyz/",
        "github": "https://github.com/coldtype",
        "youtube": "https://www.youtube.com/channel/UCIRaiGAVFaM-pSErJG1UZFA",
        "q&a forum": "https://github.com/goodhertz/coldtype/discussions",
    })

@site(ººsiblingºº(".")
    , port=8008
    , sources=dict(
        mains=partial(section, "mains"),
        tutorials=partial(section, "tutorials"),
        cheatsheets=partial(section, "cheatsheets"))
    , info=info
    , template=lambda _: "_page"
    , slugs="nested,html"
    , fonts={
        "text-font": dict(regular="MDSystem-VF"),
        "mono-font": dict(regular="MDIO-VF")})
def website(_):
    return None

def release(_):
    website.upload("coldtype.goodhertz.com", "us-east-1", None)