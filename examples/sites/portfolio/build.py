from coldtype import *

from coldtype.web.site import *
from coldtype.web.fonts import woff2s

@site(ººsiblingºº("."), 8008, info=dict(
    title="Coldtype Portfolio",
    description="This is the Coldtype portfolio",
    pages={
        "index.j2": "Home",
        "about.j2": "About",
    },
    navigation={
        "Home": "/",
        "About": "/about"
    },
    fonts=woff2s("assets", ººsiblingºº("./assets/fonts"), {
        "mono-font": dict(
            regularitalic="RecMono-CasualItalic.ttf")})))
def portfolio(_):
    return None


def exit(_):
    portfolio.kill()