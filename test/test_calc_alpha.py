from coldtype import *

@renderable()
def nested_alpha(r):
    dps = DATPens([
        DATPens([
            DATPen().oval(r.inset(50)).f(0).a(0.5)
        ]).a(0.5),
    ]).a(0.5)

    dps.walk(lambda p, i, d: None)
    assert(dps[0][0].calc_alpha() == 0.125)

    return dps