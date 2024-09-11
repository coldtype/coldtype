from coldtype import *
from coldtype.web.site import *

def public_posts(site):
    return [p for p in site.pages if p.template == "_post"]

info = dict(
    title="Coldtype Portfolio",
    description="This is the Coldtype portfolio",
    navigation={"Home": "/", "About": "/about"})

def pagemod(p):
    print(p.title)
    return p

@site(ººsiblingºº(".")
    , port=8008
    , sources=dict(public_posts=public_posts)
    , info=info
    , pagemod=pagemod
    , fonts={
        "text-font": dict(regular="Casserole-Sans")})
def portfolio(_):
    portfolio.build()

#@renderable((1080, 540), bg=1)
def test(r):
   return (StSt("TEST.A", Font.MuSan(), 400).align(r))