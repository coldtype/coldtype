from coldtype import *
import pickle

# TODO encapsulate this kind of thing as a pattern for easily editing vectors?

op = sibling(__file__, "oval.pickle")
if not op.exists():
    oval = (StyledString("COLD",
        Style("assets/ColdtypeObviously-VF.ttf", 250))
        .pen()
        .align(Rect(0, 0, 1080, 1080))
        .f(hsl(0.85)))
    pickle.dump(oval, open(op, "wb"))

@renderable(rstate=1)
def test_kb(r, rs):
    p = pickle.load(open(op, "rb"))
    if rs.cmd and rs.cmd.startswith("sc"):
        p.scale(float(rs.cmd.split(" ")[1]))
    if rs.arrow:
        p.translate(10*rs.arrow[0], 10*rs.arrow[1])
    pickle.dump(p, open(op, "wb"))
    return p

def release(_):
    op.unlink()