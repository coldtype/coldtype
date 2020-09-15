from coldtype.color import Color, Gradient
try:
    import drawBot as db
except:
    db = None


def db_fill(color):
    if color:
        if isinstance(color, Gradient):
            db_gradient(color)
        elif isinstance(color, Color):
            db.fill(color.r, color.g, color.b, color.a)
    else:
        db.fill(None)

def db_stroke(weight=1, color=None, dash=None):
    db.strokeWidth(weight)
    if dash:
        db.lineDash(dash)
    if color:
        if isinstance(color, Gradient):
            pass # possible?
        elif isinstance(color, Color):
            db.stroke(color.r, color.g, color.b, color.a)
    else:
        db.stroke(None)

def db_shadow(clip=None, radius=10, alpha=0.3, color=Color.from_rgb(0,0,0,1)):
    if clip:
        cp = DATPen(fill=None).rect(clip)
        bp = db.BezierPath()
        cp.replay(bp)
        db.clipPath(bp)
    #elif self.rect:
    #    cp = DATPen(fill=None).rect(self.rect).xor(self.dat)
    #    bp = db.BezierPath()
    #    cp.replay(bp)
    #    db.clipPath(bp)
    db.shadow((0, 0), radius*3, list(color.with_alpha(alpha)))
    
def db_gradient(gradient):
    stops = gradient.stops
    db.linearGradient(stops[0][1], stops[1][1], [list(s[0]) for s in stops], [0, 1])