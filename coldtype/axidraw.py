from coldtype.pens.axidrawpen import AxiDrawPen
from coldtype.renderable import renderable
from coldtype.pens.datpen import DATPen

"""
https://axidraw.com/doc/py_api/#installation
--> pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip
"""

def axidraw(r:renderable, tag=None, flatten=None, frame=0, test=False):
    def walker(p:DATPen, pos, _):
        if pos == 0:
            p = p.cond(flatten,
                lambda p: p.flatten(
                    flatten, segmentLines=False))
            ap = AxiDrawPen(p, r.rect)
            ap.draw()

    res = r.frame_result(frame)
    if tag:
        res = res.fft(tag)
    
    if test:
        print("-"*30)
        print("AXIDRAW TEST")
        print(">", res)
        print("-"*30)
    else:
        res.walk(walker)

class axidraw_renderable(renderable):
    def __init__(self):
        super().__init__(rect=(1100, 850))
    
    def draw(self, tag=None, flatten=10, frame=0, test=False):
        def _draw(_):
            axidraw(self, tag=tag, flatten=flatten, frame=frame, test=test)
        return _draw