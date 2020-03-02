#coding=utf-8
from __future__ import division
from math import pi, radians, degrees, tan, hypot, atan2, cos, sin

"""
Custom Robofab pens — Loïc Sander, june 2015.

The MIT License (MIT)

Copyright (c) 2014 Loïc Sander

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

from fontTools.pens.pointPen import PointToSegmentPen, SegmentToPointPen, ReverseContourPointPen
from fontTools.misc.bezierTools import splitCubicAtT
from fontTools.pens.basePen import BasePen

_ANGLE_EPSILON = pi/36


def calcVector(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    dx = x2 - x1
    dy = y2 - y1
    return dx, dy


def calcAngle(point1, point2):
    dx, dy = calcVector(point1, point2)
    return atan2(dy, dx)


def polarCoord(xy, angle, distance):
    x, y = xy
    nx = x + (distance * cos(angle))
    ny = y + (distance * sin(angle))
    return nx, ny


def calcArea(points):
    l = len(points)
    area = 0
    for i in range(l):
        x1, y1 = points[i]
        x2, y2 = points[(i+1)%l]
        area += (x1*y2)-(x2*y1)
    return area / 2


def firstDerivative(xy1, cxy1, cxy2, xy2, value):
    x1, y1 = xy1
    cx1, cy1 = cxy1
    cx2, cy2 = cxy2
    x2, y2 = xy2
    mx = bezierTangent(x1, cx1, cx2, x2, value)
    my = bezierTangent(y1, cy1, cy2, y2, value)
    return mx, my


def bezierTangent(a, b, c, d, t):
    # Implementation of http://stackoverflow.com/questions/4089443/find-the-tangent-of-a-point-on-a-cubic-bezier-curve-on-an-iphone
    return (-3*(1-t)**2 * a) + (3*(1-t)**2 * b) - (6*t*(1-t) * b) - (3*t**2 * c) + (6*t*(1-t) * c) + (3*t**2 * d)



class TranslationPen(BasePen):
    """
    Draw an outline resulting from the reunion of an initial contour and a translated version thereof.
    Translation is defined by an angle and a width/length.
    This kind of drawing basically produces a calligraphic effect (in a translated manner as Gerrit Noordzij puts it),
    it can also serve as a way of extruding a shape for 3D shadow effects.
    """

    def __init__(self, otherPen, frontAngle=0, frontWidth=20):
        self.otherPen = otherPen
        self.frontAngle = radians(frontAngle)
        self.offset = polarCoord((0, 0), radians(frontAngle), frontWidth)
        self.points = []


    def _moveTo(self, pt):
        self.points.append((pt, 'move'))


    def _lineTo(self, pt1):
        pt0, previousType = self.points[-1]
        angle = calcAngle(pt0, pt1)

        self.translatedLineSegment(pt0, pt1)

        self.points.append((pt1, 'line'))


    def _curveToOne(self, c1, c2, pt1):
        pt0, previousType = self.points[-1]

        newSegments = self.splitAtAngledExtremas(pt0, c1, c2, pt1)

        if len(newSegments):
            for segment in newSegments:
                pt0, c1, c2, pt1 = segment
                self.translatedCurveSegment(pt0, c1, c2, pt1)
        else:
            self.translatedCurveSegment(pt0, c1, c2, pt1)

        self.points.append((c1, None))
        self.points.append((c2, None))
        self.points.append((pt1, 'curve'))


    def endPath(self):
        self.points = []


    def closePath(self):
        previousPoint, previousType = self.points[-1]

        if previousType in ['line','curve']:
            pt0, pt1 = self.points[-1][0], self.points[0][0]
            self.translatedLineSegment(pt0, pt1)

        self.points = []


    def splitAtAngledExtremas(self, pt0, pt1, pt2, pt3):
        frontAngle = self.frontAngle
        segments = []
        for i in range(101):
            t = i / 100
            nx, ny = firstDerivative(pt0, pt1, pt2, pt3, t)
            tanAngle = atan2(ny, nx)
            if tan(frontAngle - _ANGLE_EPSILON) < tan(tanAngle) < tan(frontAngle + _ANGLE_EPSILON):
                newSegments = splitCubicAtT(pt0, pt1, pt2, pt3, t)
                if len(newSegments) > 1:
                    segments = newSegments
                    break
        return segments


    def translatedCurveSegment(self, pt0, c1, c2, pt1):
        ox, oy = self.offset
        x0, y0 = pt0
        xc1, yc1 = c1
        xc2, yc2 = c2
        x1, y1 = pt1
        pen = self.getPen([(x0, y0), (x1, y1), (x1+ox, y1+oy), (x0+ox, y0+oy)])
        pen.moveTo((x0, y0))
        pen.curveTo((xc1, yc1), (xc2, yc2), (x1, y1))
        pen.lineTo((x1+ox, y1+oy))
        pen.curveTo((xc2+ox, yc2+oy), (xc1+ox, yc1+oy), (x0+ox, y0+oy))
        pen.closePath()


    def translatedLineSegment(self, pt0, pt1):
        ox, oy = self.offset
        x0, y0 = pt0
        x1, y1 = pt1
        pen = self.getPen([(x0, y0), (x1, y1), (x1+ox, y1+oy), (x0+ox, y0+oy)])
        pen.moveTo((x0, y0))
        pen.lineTo((x1, y1))
        pen.lineTo((x1+ox, y1+oy))
        pen.lineTo((x0+ox, y0+oy))
        pen.closePath()


    def getPen(self, points):
        area = calcArea(points)
        if area < 0:
            pen = self.getReversePen()
        else:
            pen = self.otherPen
        return pen


    def getReversePen(self):
        adapterPen = PointToSegmentPen(self.otherPen)
        reversePen = ReverseContourPointPen(adapterPen)
        return SegmentToPointPen(reversePen)


    def addComponent(self, baseGlyphName, transformation):
        self.otherPen.addComponent(baseGlyphName, transformation)