from coldtype import *
import pickle

# TODO encapsulate this kind of thing as a pattern for easily editing vectors?

op = sibling(__file__, "oval.pickle")
if not op.exists():
    oval = (DATPen()
        .oval(Rect(0, 0, 1000, 1000))
        .f(hsl(random()))
        .scale(0.5))
    pickle.dump(oval, open(op, "wb"))

@renderable(rstate=1)
def test_kb(r, rs):
    p = pickle.load(open(op, "rb"))
    if rs.cmd and rs.cmd.startswith("sc"):
        p.scale(float(rs.cmd.split(" ")[1]))
    pickle.dump(p, open(op, "wb"))
    return p

def release(_):
    op.unlink()