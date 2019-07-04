# Mixin for attribute-application
from grapefruit import Color
from random import random


class DrawablePenMixin(object):
    def fill(self, el, color):
        raise Exception("Pen does not implement fill function")
    
    def stroke(self, el, weight=1, color=None):
        raise Exception("Pen does not implement stroke function")

    def shadow(self, el, clip=None, radius=10, alpha=0.3):
        raise Exception("Pen does not implement shadow function")

    def image(self, el, src=None, opacity=None, rect=None):
        raise Exception("Pen does not implement image function")

    def applyDATAttribute(self, attribute):
        k, v = attribute
        if k == "shadow":
            self.shadow(**v)
        elif k == "fill":
            self.fill(v)
        elif k == "stroke":
            self.stroke(**v)
        elif k == "image":
            self.image(**v)


def normalize_color(v):
        if v is None:
            return Color.from_rgb(0,0,0,0)
        elif isinstance(v, Color):
            return v
        elif isinstance(v, Gradient):
            return v
        elif isinstance(v, float) or isinstance(v, int):
            return Color.from_rgb(v, v, v)
        elif isinstance(v, str):
            if v == "random":
                return Color.from_rgb(random(), random(), random())
            elif v == "none":
                return Color.from_rgb(0,0,0,0)
            else:
                return Color.from_html(v)
        else:
            if len(v) == 1:
                return Color.from_rgb(v[0], v[0], v[0])
            elif len(v) == 2:
                if v[0] == "random":
                    return Color.from_rgb(random(), random(), random(), v[1])
                elif isinstance(v[0], str):
                    return Color.from_html(v[0]).with_alpha(v[1])
                else:
                    print("v", v)
                    return Color.from_rgb(v[0], v[0], v[0], v[1])
            else:
                return Color.from_rgb(*v)


class Gradient():
    def __init__(self, *stops):
        self.stops = []
        for c, p in stops:
            self.addStop(c, p)
    
    def addStop(self, color, point):
        self.stops.append([normalize_color(color), point])
    
    def Vertical(rect, a, b):
        return Gradient([a, rect.point("N")], [b, rect.point("S")])
    
    def Horizontal(rect, a, b):
        return Gradient([a, rect.point("E")], [b, rect.point("W")])