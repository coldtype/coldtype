from coldtype import *
import pickle

op = __sibling__("oval.pickle")
if not op.exists():
    oval = (StyledString("L",
        Style("assets/ColdtypeObviously_BlackItalic.ufo", 1000))
        .pen()
        .align(Rect(0, 0, 1080, 1080))
        .f(0))
    pickle.dump(oval, open(op, "wb"))

@renderable(rstate=1)
def test_kb(r, rs):
    p = pickle.load(open(op, "rb"))
    out = DATPens([p])

    if rs.keylayer == Keylayer.Editing:
        pt_lookup = p.points_lookup()
        if rs.arrow and rs.xray:
            rs.increment_selection(rs.arrow[0], len(pt_lookup))
        
        for idx, pl in enumerate(pt_lookup):
            pt = pl.get("pt")
            if idx in rs.selection:
                if rs.arrow and not rs.xray and not rs.mods.ctrl:
                    pt = p.mod_point(pt_lookup, idx, *rs.arrow)

                out += (DATPen()
                    .oval(Rect(pt[0]-50, pt[1]-50, 100, 100))
                    .f(None)
                    .s(hsl(0.65, s=1, l=0.65, a=1 if rs.xray else 0.25))
                    .sw(10 if rs.xray else 1))
            
            if rs.xray:
                out += (DATPen()
                    .oval(Rect(pt[0]-10, pt[1]-10, 20, 20))
                    .f(hsl(0.95 if idx in rs.selection else 0.75, a=0.5))
                    .scale(1.5 if idx in rs.selection else 1))
            
        if rs.mouse:
            out += (DATPen()
                .oval(Rect.FromCenter(rs.mouse, 100))
                .f(hsl(random(), a=0.5)))
    
    pickle.dump(p, open(op, "wb"))

    if rs.keylayer == Keylayer.Editing:
        p.f(hsl(0.65, a=0.25)).s(0).sw(3)
    return out

def release(_):
    op.unlink()