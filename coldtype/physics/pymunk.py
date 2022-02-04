import pymunk
from coldtype.runon.path import P


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