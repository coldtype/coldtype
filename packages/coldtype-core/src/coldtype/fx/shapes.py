import math

def sine(r, periods):
    """Sine-wave primitive"""
    def _record(pen):
        dp = type(pen)()
        pw = r.w / periods
        p1 = r.point("SW")
        end = r.point("SE")
        dp.moveTo(p1)
        done = False
        up = True
        while not done:
            h = r.h if up else -r.h
            c1 = p1.offset(pw/2, 0)
            c2 = p1.offset(pw/2, h)
            p2 = p1.offset(pw, h)
            dp.curveTo(c1, c2, p2)
            p1 = p2
            if p1.x >= end.x:
                done = True
            else:
                done = False
            up = not up
        pen.record(dp)
    return _record
    

def standingwave(r, periods, direction=1):
    """Standing-wave primitive"""
    def _record(pen):
        dp = type(pen)()

        blocks = r.subdivide(periods, "minx")
        for idx, block in enumerate(blocks):
            n, e, s, w = block.take(1, "centery").cardinals()
            if idx == 0:
                dp.moveTo(w)
            if direction == 1:
                if idx%2 == 0:
                    dp.lineTo(n)
                else:
                    dp.lineTo(s)
            else:
                if idx%2 == 0:
                    dp.lineTo(s)
                else:
                    dp.lineTo(n)
            if idx == len(blocks) - 1:
                dp.lineTo(e)
        dp.endPath().smooth()
        dp.value = dp.value[:-1]
        dp.endPath()
        pen.record(dp)
    return _record


def polygon(sides, rect):
    """Polygon primitive; WIP"""
    def _record(pen):
        radius = rect.square().w / 2
        c = rect.center()
        one_segment = math.pi * 2 / sides
        points = [(math.sin(one_segment * i) * radius, math.cos(one_segment * i) * radius) for i in range(sides)]
        dp = type(pen)()
        points.reverse()
        dp.moveTo(points[0])
        for p in points[1:]:
            dp.lineTo(p)
        dp.closePath()
        dp.align(rect)
        pen.record(dp)
    return _record


def _lissajous_points(a, b, phase, radius, num_steps=340):
    """I believe originally by Just van Rossum, via Very Cool Studio"""
    points = []
    for i in range(num_steps):
        angle = 2 * math.pi * i / num_steps
        x = radius * math.sin(a * angle + phase)
        y = -radius * math.sin(b * angle)
        points.append((x, y))
    return points


def lissajous(a, b, phase_t, radius, num_steps=340, autophase=True):
    """draw a lissajous curve on the pen, though you'll probably need to align it"""
    def _lissajous(pen):
        return (pen
            .line(_lissajous_points(a, b,
                2 * math.pi * phase_t if autophase else phase_t,
                radius, num_steps))
            .closePath())
    return _lissajous