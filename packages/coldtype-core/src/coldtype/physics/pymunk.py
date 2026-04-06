import pymunk
from coldtype.runon.path import P


def polygon(samples=5):
    def _polygon(p:P):
        pts = list(map(lambda x: x.pt.xy(), p.pen().samples(samples)))
        pmass = 3.0
        pmoment = pymunk.moment_for_poly(pmass, pts)
        pbody = pymunk.Body(pmass, pmoment)
        pshape = pymunk.Poly(pbody, pts)
        pshape.friction = 0.01
        pshape.elasticity = 0.9
        pshape.collision_type = 0
        return pbody, pshape
    return _polygon


def segments(body, flatten=30):
    def _segments(p:P):
        p = p.copy().pen().removeOverlap()
        if flatten:
            p = p.flatten(flatten)
        
        segs = []
        for line in p.segments():
            p1, p2 = line.v.value[0][ 1][0], line.v.value[1][1][0]
            segs.append(pymunk.Segment(body, p1, p2, 0.0))
        return segs
    return _segments