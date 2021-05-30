from coldtype import *

@animation(storyboard=[1])
def anim(f):
    return (DATPen()
        .oval(f.a.r.inset(50+f.i*10))
        .f(0.8)) + DATText(str(f.i), Style("Times", 100, load_font=0), f.a.r.inset(100))
