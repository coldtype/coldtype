from coldtype import *

from coldtype.web.site import *
from coldtype.web.fonts import woff2s

def public_posts(site):
    return [p for p in site.pages if p.template == "_post"]

info = dict(
    title="Coldtype Portfolio",
    description="This is the Coldtype portfolio",
    pages={
        "index.j2": "Home",
        "about.j2": "About",
    },
    navigation={"Home": "/", "About": "/about"},
    fonts=woff2s(
        ººsiblingºº("./assets/fonts"),
        {"mono-font": dict(regularitalic="Casserole-Sans")},
    ),
)

@site(ººsiblingºº(".")
      , port=8008
      , sources=dict(public_posts=public_posts)
      , info=info)
def portfolio(_):
    return None

@renderable((1080, 540), bg=1, solo=1)
def test(r):
   return (StSt("TEST.A", Font.MuSan(), 400).align(r))