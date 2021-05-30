"""
The MIT License (MIT)

Copyright (c) 2016 Frederik Berlaen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Taken from https://github.com/typemytype/outlinerRoboFontExtension
"""

from fontTools.pens.basePen import BasePen
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.ufoLib.pointPen import AbstractPointPen, ReverseContourPointPen
from fontTools.misc.bezierTools import splitCubicAtT
from math import sqrt, cos, sin, acos, asin, degrees, radians, pi

try:
    from defcon import Glyph
except:
    pass


def roundFloat(f):
    error = 1000000.
    return round(f*error)/error


def checkSmooth(firstAngle, lastAngle):
    if firstAngle is None or lastAngle is None:
        return True
    error = 4
    firstAngle = degrees(firstAngle)
    lastAngle = degrees(lastAngle)

    if int(firstAngle) + error >= int(lastAngle) >= int(firstAngle) - error:
        return True
    return False


def checkInnerOuter(firstAngle, lastAngle):
    if firstAngle is None or lastAngle is None:
        return True
    dirAngle = degrees(firstAngle) - degrees(lastAngle)

    if dirAngle > 180:
        dirAngle = 180 - dirAngle
    elif dirAngle < -180:
        dirAngle = -180 - dirAngle

    if dirAngle > 0:
        return True

    if dirAngle <= 0:
        return False


def interSect(seg1, seg2):
    seg1s, seg1e = seg1
    seg2s, seg2e = seg2
    denom = (seg2e.y - seg2s.y)*(seg1e.x - seg1s.x) - (seg2e.x - seg2s.x)*(seg1e.y - seg1s.y)
    if roundFloat(denom) == 0:
        # print('parallel: %s' % denom)
        return None
    uanum = (seg2e.x - seg2s.x)*(seg1s.y - seg2s.y) - (seg2e.y - seg2s.y)*(seg1s.x - seg2s.x)
    ubnum = (seg1e.x - seg1s.x)*(seg1s.y - seg2s.y) - (seg1e.y - seg1s.y)*(seg1s.x - seg2s.x)
    ua = uanum / denom
    # ub = ubnum / denom
    x = seg1s.x + ua*(seg1e.x - seg1s.x)
    y = seg1s.y + ua*(seg1e.y - seg1s.y)
    return MathPoint(x, y)


def pointOnACurve(p1, c1, c2, p2, value):
    x1, y1 = p1
    cx1, cy1 = c1
    cx2, cy2 = c2
    x2, y2 = p2
    dx = x1
    cx = (cx1 - dx) * 3.0
    bx = (cx2 - cx1) * 3.0 - cx
    ax = x2 - dx - cx - bx
    dy = y1
    cy = (cy1 - dy) * 3.0
    by = (cy2 - cy1) * 3.0 - cy
    ay = y2 - dy - cy - by
    mx = ax*(value)**3 + bx*(value)**2 + cx*(value) + dx
    my = ay*(value)**3 + by*(value)**2 + cy*(value) + dy
    return MathPoint(mx, my)


class MathPoint(object):

    def __init__(self, x, y=None):
        if y is None:
            x, y = x
        self.x = x
        self.y = y

    def __repr__(self):
        return "<MathPoint x:%s y:%s>" % (self.x, self.y)

    def __getitem__(self, index):
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        raise IndexError

    def __iter__(self):
        for value in [self.x, self.y]:
            yield value

    def __add__(self, p):  # p + p
        if not isinstance(p, self.__class__):
            return self.__class__(self.x + p, self.y + p)
        return self.__class__(self.x + p.x, self.y + p.y)

    def __sub__(self, p):  # p - p
        if not isinstance(p, self.__class__):
            return self.__class__(self.x - p, self.y - p)
        return self.__class__(self.x - p.x, self.y - p.y)

    def __mul__(self, p):  # p * p
        if not isinstance(p, self.__class__):
            return self.__class__(self.x * p, self.y * p)
        return self.__class__(self.x * p.x, self.y * p.y)

    def __div__(self, p):  # p / p
        if not isinstance(p, self.__class__):
            return self.__class__(self.x / p, self.y / p)
        return self.__class__(self.x / p.x, self.y / p.y)

    def __eq__(self, p):  # if p == p
        if not isinstance(p, self.__class__):
            return False
        return roundFloat(self.x) == roundFloat(p.x) and roundFloat(self.y) == roundFloat(p.y)

    def __ne__(self, p):  # if p != p
        return not self.__eq__(p)

    def copy(self):
        return self.__class__(self.x, self.y)

    def round(self):
        self.x = round(self.x)
        self.y = round(self.y)

    def distance(self, p):
        return sqrt((p.x - self.x)**2 + (p.y - self.y)**2)

    def angle(self, other, add=90):
        # returns the angle of a Line in radians
        b = other.x - self.x
        a = other.y - self.y
        c = sqrt(a**2 + b**2)
        if c == 0:
            return None
        if add is None:
            return b/c
        cosAngle = degrees(acos(b/c))
        sinAngle = degrees(asin(a/c))
        if sinAngle < 0:
            cosAngle = 360 - cosAngle
        return radians(cosAngle + add)


class CleanPointPen(AbstractPointPen):

    def __init__(self, pointPen):
        self.pointPen = pointPen
        self.currentContour = None

    def processContour(self):
        pointPen = self.pointPen
        contour = self.currentContour

        index = 0
        prevAngle = None
        toRemove = []
        for data in contour:
            if data["segmentType"] in ["line", "move"]:
                prevPoint = contour[index-1]
                if prevPoint["segmentType"] in ["line", "move"]:
                    angle = MathPoint(data["point"]).angle(MathPoint(prevPoint["point"]))
                    if prevAngle is not None and angle is not None and roundFloat(prevAngle) == roundFloat(angle):
                        prevPoint["uniqueID"] = id(prevPoint)
                        toRemove.append(prevPoint)
                    prevAngle = angle
                else:
                    prevAngle = None
            else:
                prevAngle = None
            index += 1

        for data in toRemove:
            contour.remove(data)

        pointPen.beginPath()
        for data in contour:
            pointPen.addPoint(data["point"], **data)
        pointPen.endPath()

    def beginPath(self, identifier=None):
        assert self.currentContour is None
        self.currentContour = []
        self.onCurve = []

    def endPath(self):
        assert self.currentContour is not None
        self.processContour()
        self.currentContour = None

    def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
        data = dict(point=pt, segmentType=segmentType, smooth=smooth, name=name)
        data.update(kwargs)
        self.currentContour.append(data)

    def addComponent(self, glyphName, transform):
        assert self.currentContour is None
        self.pointPen.addComponent(glyphName, transform)


class OutlinePen(BasePen):

    pointClass = MathPoint
    magicCurve = 0.5522847498

    def __init__(self, glyphSet, offset=10, contrast=0, contrastAngle=0, connection="square", cap="round", miterLimit=None, closeOpenPaths=True, optimizeCurve=False, preserveComponents=False, filterDoubles=True):
        BasePen.__init__(self, glyphSet)

        self.offset = abs(offset)
        self.contrast = abs(contrast)
        self.contrastAngle = contrastAngle
        self._inputmiterLimit = miterLimit
        if miterLimit is None:
            miterLimit = self.offset * 2
        self.miterLimit = abs(miterLimit)

        self.closeOpenPaths = closeOpenPaths
        self.optimizeCurve = optimizeCurve

        self.connectionCallback = getattr(self, "connection%s" % (connection.title()))
        self.capCallback = getattr(self, "cap%s" % (cap.title()))

        self.originalGlyph = Glyph()
        self.originalPen = self.originalGlyph.getPen()

        self.outerGlyph = Glyph()
        self.outerPen = self.outerGlyph.getPen()
        self.outerCurrentPoint = None
        self.outerFirstPoint = None
        self.outerPrevPoint = None

        self.innerGlyph = Glyph()
        self.innerPen = self.innerGlyph.getPen()
        self.innerCurrentPoint = None
        self.innerFirstPoint = None
        self.innerPrevPoint = None

        self.prevPoint = None
        self.firstPoint = None
        self.firstAngle = None
        self.prevAngle = None

        self.shouldHandleMove = True

        self.preserveComponents = preserveComponents
        self.components = []

        self.filterDoubles = filterDoubles
        self.drawSettings()

    def _moveTo(self, pt):
        x, y = pt
        if self.offset == 0:
            self.outerPen.moveTo((x, y))
            self.innerPen.moveTo((x, y))
            return
        self.originalPen.moveTo((x, y))

        p = self.pointClass(x, y)
        self.prevPoint = p
        self.firstPoint = p
        self.shouldHandleMove = True

    def _lineTo(self, pt):
        x, y = pt
        if self.offset == 0:
            self.outerPen.lineTo((x, y))
            self.innerPen.lineTo((x, y))
            return
        self.originalPen.lineTo((x, y))

        currentPoint = self.pointClass(x, y)
        if currentPoint == self.prevPoint:
            return

        self.currentAngle = self.prevPoint.angle(currentPoint)
        thickness = self.getThickness(self.currentAngle)
        self.innerCurrentPoint = self.prevPoint - self.pointClass(cos(self.currentAngle), sin(self.currentAngle)) * thickness
        self.outerCurrentPoint = self.prevPoint + self.pointClass(cos(self.currentAngle), sin(self.currentAngle)) * thickness

        if self.shouldHandleMove:
            self.shouldHandleMove = False

            self.innerPen.moveTo(self.innerCurrentPoint)
            self.innerFirstPoint = self.innerCurrentPoint

            self.outerPen.moveTo(self.outerCurrentPoint)
            self.outerFirstPoint = self.outerCurrentPoint

            self.firstAngle = self.currentAngle
        else:
            self.buildConnection()

        self.innerCurrentPoint = currentPoint - self.pointClass(cos(self.currentAngle), sin(self.currentAngle)) * thickness
        self.innerPen.lineTo(self.innerCurrentPoint)
        self.innerPrevPoint = self.innerCurrentPoint

        self.outerCurrentPoint = currentPoint + self.pointClass(cos(self.currentAngle), sin(self.currentAngle)) * thickness
        self.outerPen.lineTo(self.outerCurrentPoint)
        self.outerPrevPoint = self.outerCurrentPoint

        self.prevPoint = currentPoint
        self.prevAngle = self.currentAngle

    def _curveToOne(self, pt1, pt2, pt3):
        if self.optimizeCurve:
            curves = splitCubicAtT(self.prevPoint, pt1, pt2, pt3, .5)
        else:
            curves = [(self.prevPoint, pt1, pt2, pt3)]
        for curve in curves:
            p1, h1, h2, p2 = curve
            self._processCurveToOne(h1, h2, p2)

    def _processCurveToOne(self, pt1, pt2, pt3):
        if self.offset == 0:
            self.outerPen.curveTo(pt1, pt2, pt3)
            self.innerPen.curveTo(pt1, pt2, pt3)
            return
        self.originalPen.curveTo(pt1, pt2, pt3)

        p1 = self.pointClass(*pt1)
        p2 = self.pointClass(*pt2)
        p3 = self.pointClass(*pt3)

        if p1 == self.prevPoint:
            p1 = pointOnACurve(self.prevPoint, p1, p2, p3, 0.01)
        if p2 == p3:
            p2 = pointOnACurve(self.prevPoint, p1, p2, p3, 0.99)

        a1 = self.prevPoint.angle(p1)
        a2 = p2.angle(p3)

        self.currentAngle = a1
        tickness1 = self.getThickness(a1)
        tickness2 = self.getThickness(a2)

        a1bis = self.prevPoint.angle(p1, 0)
        a2bis = p3.angle(p2, 0)
        intersectPoint = interSect((self.prevPoint, self.prevPoint + self.pointClass(cos(a1), sin(a1)) * 100),
                                   (p3, p3 + self.pointClass(cos(a2), sin(a2)) * 100))
        self.innerCurrentPoint = self.prevPoint - self.pointClass(cos(a1), sin(a1)) * tickness1
        self.outerCurrentPoint = self.prevPoint + self.pointClass(cos(a1), sin(a1)) * tickness1

        if self.shouldHandleMove:
            self.shouldHandleMove = False

            self.innerPen.moveTo(self.innerCurrentPoint)
            self.innerFirstPoint = self.innerPrevPoint = self.innerCurrentPoint

            self.outerPen.moveTo(self.outerCurrentPoint)
            self.outerFirstPoint = self.outerPrevPoint = self.outerCurrentPoint

            self.firstAngle = a1
        else:
            self.buildConnection()

        h1 = None
        if intersectPoint is not None:
            h1 = interSect((self.innerCurrentPoint, self.innerCurrentPoint + self.pointClass(cos(a1bis), sin(a1bis)) * tickness1),  (intersectPoint, p1))
        if h1 is None:
            h1 = p1 - self.pointClass(cos(a1), sin(a1)) * tickness1

        self.innerCurrentPoint = p3 - self.pointClass(cos(a2), sin(a2)) * tickness2

        h2 = None
        if intersectPoint is not None:
            h2 = interSect((self.innerCurrentPoint, self.innerCurrentPoint + self.pointClass(cos(a2bis), sin(a2bis)) * tickness2), (intersectPoint, p2))
        if h2 is None:
            h2 = p2 - self.pointClass(cos(a1), sin(a1)) * tickness1

        self.innerPen.curveTo(h1, h2, self.innerCurrentPoint)
        self.innerPrevPoint = self.innerCurrentPoint

        ########
        h1 = None
        if intersectPoint is not None:
            h1 = interSect((self.outerCurrentPoint, self.outerCurrentPoint + self.pointClass(cos(a1bis), sin(a1bis)) * tickness1), (intersectPoint, p1))
        if h1 is None:
            h1 = p1 + self.pointClass(cos(a1), sin(a1)) * tickness1

        self.outerCurrentPoint = p3 + self.pointClass(cos(a2), sin(a2)) * tickness2

        h2 = None
        if intersectPoint is not None:
            h2 = interSect((self.outerCurrentPoint, self.outerCurrentPoint + self.pointClass(cos(a2bis), sin(a2bis)) * tickness2), (intersectPoint, p2))
        if h2 is None:
            h2 = p2 + self.pointClass(cos(a1), sin(a1)) * tickness1
        self.outerPen.curveTo(h1, h2, self.outerCurrentPoint)
        self.outerPrevPoint = self.outerCurrentPoint

        self.prevPoint = p3
        self.currentAngle = a2
        self.prevAngle = a2

    def _closePath(self):
        if self.shouldHandleMove:
            return
        if self.offset == 0:
            self.outerPen.closePath()
            self.innerPen.closePath()
            return

        if not self.prevPoint == self.firstPoint:
            self._lineTo(self.firstPoint)

        self.originalPen.closePath()

        self.innerPrevPoint = self.innerCurrentPoint
        self.innerCurrentPoint = self.innerFirstPoint

        self.outerPrevPoint = self.outerCurrentPoint
        self.outerCurrentPoint = self.outerFirstPoint

        self.prevAngle = self.currentAngle
        self.currentAngle = self.firstAngle

        self.buildConnection(close=True)

        self.innerPen.closePath()
        self.outerPen.closePath()

    def _endPath(self):
        if self.shouldHandleMove:
            return

        self.originalPen.endPath()
        self.innerPen.endPath()
        self.outerPen.endPath()

        if self.closeOpenPaths:

            innerContour = self.innerGlyph[-1]
            outerContour = self.outerGlyph[-1]

            innerContour.reverse()

            innerContour[0].segmentType = "line"
            outerContour[0].segmentType = "line"

            self.buildCap(outerContour, innerContour)

            for point in innerContour:
                outerContour.addPoint((point.x, point.y), segmentType=point.segmentType, smooth=point.smooth)

            self.innerGlyph.removeContour(innerContour)

    def addComponent(self, glyphName, transform):
        if self.preserveComponents:
            self.components.append((glyphName, transform))
        else:
            BasePen.addComponent(self, glyphName, transform)

    # thickness

    def getThickness(self, angle):
        a2 = angle + pi * .5
        f = abs(sin(a2 + radians(self.contrastAngle)))
        f = f ** 5
        return self.offset + self.contrast * f

    # connections

    def buildConnection(self, close=False):
        if not checkSmooth(self.prevAngle, self.currentAngle):
            if checkInnerOuter(self.prevAngle, self.currentAngle):
                self.connectionCallback(self.outerPrevPoint, self.outerCurrentPoint, self.outerPen, close)
                self.connectionInnerCorner(self.innerPrevPoint, self.innerCurrentPoint, self.innerPen, close)
            else:
                self.connectionCallback(self.innerPrevPoint, self.innerCurrentPoint, self.innerPen, close)
                self.connectionInnerCorner(self.outerPrevPoint, self.outerCurrentPoint, self.outerPen, close)
        elif not self.filterDoubles:
            self.innerPen.lineTo(self.innerCurrentPoint)
            self.outerPen.lineTo(self.outerCurrentPoint)
    
    def connectionSquare(self, first, last, pen, close):
        angle_1 = radians(degrees(self.prevAngle)+90)
        angle_2 = radians(degrees(self.currentAngle)+90)

        tempFirst = first - self.pointClass(cos(angle_1), sin(angle_1)) * self.miterLimit
        tempLast = last + self.pointClass(cos(angle_2), sin(angle_2)) * self.miterLimit

        newPoint = interSect((first, tempFirst), (last, tempLast))

        if newPoint is not None:

            if self._inputmiterLimit is not None and roundFloat(newPoint.distance(first)) > self._inputmiterLimit:
                pen.lineTo(tempFirst)
                pen.lineTo(tempLast)
            else:
                pen.lineTo(newPoint)

        if not close:
            pen.lineTo(last)

    def connectionRound(self, first, last, pen, close):
        angle_1 = radians(degrees(self.prevAngle)+90)
        angle_2 = radians(degrees(self.currentAngle)+90)

        tempFirst = first - self.pointClass(cos(angle_1), sin(angle_1)) * self.miterLimit
        tempLast = last + self.pointClass(cos(angle_2), sin(angle_2)) * self.miterLimit

        newPoint = interSect((first, tempFirst), (last, tempLast))
        if newPoint is None:
            pen.lineTo(last)
            return
        distance1 = newPoint.distance(first)
        distance2 = newPoint.distance(last)
        if roundFloat(distance1) > self.miterLimit + self.contrast:
            distance1 = self.miterLimit + tempFirst.distance(tempLast) * .7
        if roundFloat(distance2) > self.miterLimit + self.contrast:
            distance2 = self.miterLimit + tempFirst.distance(tempLast) * .7

        distance1 *= self.magicCurve
        distance2 *= self.magicCurve

        bcp1 = first - self.pointClass(cos(angle_1), sin(angle_1)) * distance1
        bcp2 = last + self.pointClass(cos(angle_2), sin(angle_2)) * distance2
        pen.curveTo(bcp1, bcp2, last)

    def connectionButt(self, first, last, pen, close):
        if not close:
            pen.lineTo(last)

    def connectionInnerCorner(self, first, last, pen, close):
        if not close:
            pen.lineTo(last)

    # caps

    def buildCap(self, firstContour, lastContour):
        first = firstContour[-1]
        last = lastContour[0]
        first = self.pointClass(first.x, first.y)
        last = self.pointClass(last.x, last.y)

        self.capCallback(firstContour, lastContour, first, last, self.prevAngle)

        first = lastContour[-1]
        last = firstContour[0]
        first = self.pointClass(first.x, first.y)
        last = self.pointClass(last.x, last.y)

        angle = radians(degrees(self.firstAngle) + 180)
        self.capCallback(lastContour, firstContour, first, last, angle)

    def capButt(self, firstContour, lastContour, first, last, angle):
        # not nothing
        pass

    def capRound(self, firstContour, lastContour, first, last, angle):
        hookedAngle = radians(degrees(angle) + 90)

        p1 = first - self.pointClass(cos(hookedAngle), sin(hookedAngle)) * self.offset

        p2 = last - self.pointClass(cos(hookedAngle), sin(hookedAngle)) * self.offset

        oncurve = p1 + (p2 - p1) * .5

        roundness = .54

        h1 = first - self.pointClass(cos(hookedAngle), sin(hookedAngle)) * self.offset * roundness
        h2 = oncurve + self.pointClass(cos(angle), sin(angle)) * self.offset * roundness

        firstContour[-1].smooth = True

        firstContour.addPoint((h1.x, h1.y))
        firstContour.addPoint((h2.x, h2.y))
        firstContour.addPoint((oncurve.x, oncurve.y), smooth=True, segmentType="curve")

        h1 = oncurve - self.pointClass(cos(angle), sin(angle)) * self.offset * roundness
        h2 = last - self.pointClass(cos(hookedAngle), sin(hookedAngle)) * self.offset * roundness

        firstContour.addPoint((h1.x, h1.y))
        firstContour.addPoint((h2.x, h2.y))

        lastContour[0].segmentType = "curve"
        lastContour[0].smooth = True

    def capSquare(self, firstContour, lastContour, first, last, angle):
        angle = radians(degrees(angle) + 90)

        firstContour[-1].smooth = True
        lastContour[0].smooth = True

        p1 = first - self.pointClass(cos(angle), sin(angle)) * self.offset
        firstContour.addPoint((p1.x, p1.y), smooth=False, segmentType="line")

        p2 = last - self.pointClass(cos(angle), sin(angle)) * self.offset
        firstContour.addPoint((p2.x, p2.y), smooth=False, segmentType="line")

    def drawSettings(self, drawOriginal=False, drawInner=False, drawOuter=True):
        self.drawOriginal = drawOriginal
        self.drawInner = drawInner
        self.drawOuter = drawOuter

    def drawPoints(self, pointPen):
        if self.drawInner:
            reversePen = ReverseContourPointPen(pointPen)
            self.innerGlyph.drawPoints(CleanPointPen(reversePen))
        if self.drawOuter:
            self.outerGlyph.drawPoints(CleanPointPen(pointPen))

        if self.drawOriginal:
            if self.drawOuter:
                pointPen = ReverseContourPointPen(pointPen)
            self.originalGlyph.drawPoints(CleanPointPen(pointPen))

        for glyphName, transform in self.components:
            pointPen.addComponent(glyphName, transform)

    def draw(self, pen):
        pointPen = PointToSegmentPen(pen)
        self.drawPoints(pointPen)

    def getGlyph(self):
        glyph = Glyph()
        pointPen = glyph.getPointPen()
        self.drawPoints(pointPen)
        return glyph
    
    def Record(recording, offset=1):
        op = OutlinePen(None, offset=offset, optimizeCurve=True)
        replayRecording(recording.value, op)
        op.drawSettings(drawInner=True, drawOuter=True)
        g = op.getGlyph()
        rp2 = RecordingPen()
        g.draw(rp2)
        return rp2