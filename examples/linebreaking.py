from coldtype import *

txt = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque at aliquet neque, non bibendum nisi. Mauris quis ligula felis."

@renderable(bg=1)
def scratch(r):
    ri = r.inset(50)
    return (StSt(txt, Font.JBMono(), 70)
        .wordPens()
        .linebreak(ri.w)
        .stack("100%")
        .align(ri)
        .f(0))
