from fontTools.pens.recordingPen import RecordingPen, replayRecording


class CurveCutter():
    def __init__(self, g, inc=0.0015):
        self.pen = RecordingPen()
        g.draw(self.pen)
        self.inc = inc
        self.length = self.calcCurveLength()
    
    def calcCurveLength(self):
        length = 0
        for i, (t, pts) in enumerate(self.pen.value):
            if t == "curveTo":
                p1, p2, p3 = pts
                p0 = self.pen.value[i-1][-1][-1]
                length += calcCubicArcLength(p0, p1, p2, p3)
            elif t == "lineTo":
                pass # todo
        return length

    def subsegment(self, start=None, end=None):
        inc = self.inc
        length = self.length
        ended = False
        _length = 0
        out = []
        for i, (t, pts) in enumerate(self.pen.value):
            if t == "curveTo":
                p1, p2, p3 = pts
                p0 = self.pen.value[i-1][-1][-1]
                length_arc = calcCubicArcLength(p0, p1, p2, p3)
                if _length + length_arc < end:
                    _length += length_arc
                else:
                    t = inc
                    tries = 0
                    while not ended:
                        a, b = splitCubicAtT(p0, p1, p2, p3, t)
                        length_a = calcCubicArcLength(*a)
                        if _length + length_a > end:
                            ended = True
                            out.append(("curveTo", a[1:]))
                        else:
                            t += inc
                            tries += 1
            if t == "lineTo":
                pass # TODO
            if not ended:
                out.append((t, pts))
    
        if out[-1][0] != "endPath":
            out.append(("endPath",[]))
        return out

    def subsegmentPoint(self, start=0, end=1):
        inc = self.inc
        subsegment = self.subsegment(start=start, end=end)
        try:
            t, (a, b, c) = subsegment[-2]
            tangent = math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) + math.pi*.5)
            return c, tangent
        except ValueError:
            return None, None