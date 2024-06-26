from coldtype import *

from coldtype.web.site import *
from coldtype.web.fonts import woff2s

info = dict(
    title="Coldtype Portfolio",
    description="This is the Coldtype portfolio",
    pages={
        "index.j2": "Home",
        "about.j2": "About",
    },
    navigation={"Home": "/", "About": "/about"},
    fonts=woff2s(
        "assets",
        ººsiblingºº("./assets/fonts"),
        {"mono-font": dict(regularitalic="RecMono-CasualItalic.ttf")},
    ),
)


@site(ººsiblingºº(".")
      , port=8008
      , multiport=8009
      , info=info)
def portfolio(_):
    return None