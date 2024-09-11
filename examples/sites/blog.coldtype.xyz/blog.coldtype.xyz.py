from coldtype import *
from coldtype.web.site import *

def public_posts(site):
    return list(reversed(sorted([p for p in site.pages if p.template == "_post"], key=lambda p: p.date)))

info = dict(
    title="The Coldtype Blog",
    description="This is the Coldtype blog",
    navigation={
        "Home": "/",
        #"About": "/about"
    })

@site(ººsiblingºº(".")
    , port=8008
    , sources=dict(public_posts=public_posts)
    , info=info
    , fonts={
        "text-font": dict(regular="MDSystem-VF"),
        "mono-font": dict(regular="MDIO-VF")})
def website(_):
    website.build()

def release(_):
    website.upload("blog.coldtype.xyz", "us-west-1", "personal")