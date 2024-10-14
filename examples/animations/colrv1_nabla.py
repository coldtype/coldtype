from coldtype import *

@animation((1080, 540), tl=30, bg=hsl(0.7, 0.4, 0.4))
def nabla1(f):
    return (Glyphwise("COLRv1", lambda x:
        Style("Nabla-Regular-VariableFont_EDPT,EHLT", 300
            , EDPT=f.adj(x.i*20).e("eei", r=(0.1, 1))))
        .align(f.a.r, tx=0, ty=0)
        .translate(0, -30))