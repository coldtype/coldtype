from coldtype.pens.draftingpen import DraftingPen
from coldtype.color import hsl


def cubicBezier(x1, y1, x2, y2):
    p = DraftingPen()
    p.moveTo((0, 0))
    p.curveTo((x1*1000, y1*1000), (x2*1000, y2*1000), (1000, 1000))
    p.endPath()
    return p.fssw(-1, hsl(0.6), 2)