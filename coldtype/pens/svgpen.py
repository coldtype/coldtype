from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import BasePen

from coldtype.color import Gradient, Color
from coldtype.pens.drawablepen import DrawablePenMixin

from coldtype.color import Color
from lxml import etree
import base64

from random import randint


def pointToString(pt):
    return " ".join(["{:0.1f}".format(i) for i in pt])


class SVGPathPen(BasePen):

    def __init__(self, glyphSet):
        BasePen.__init__(self, glyphSet)
        self._commands = []
        self._lastCommand = None
        self._lastX = None
        self._lastY = None

    def _handleAnchor(self):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((0, 0))
        >>> pen.moveTo((10, 10))
        >>> pen._commands
        ['M10 10']
        """
        if self._lastCommand == "M":
            self._commands.pop(-1)

    def _moveTo(self, pt):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((0, 0))
        >>> pen._commands
        ['M0 0']
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((10, 0))
        >>> pen._commands
        ['M10 0']
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((0, 10))
        >>> pen._commands
        ['M0 10']
        """
        self._handleAnchor()
        t = "M%s" % (pointToString(pt))
        self._commands.append(t)
        self._lastCommand = "M"
        self._lastX, self._lastY = pt

    def _lineTo(self, pt):
        """
        # duplicate point
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((10, 10))
        >>> pen.lineTo((10, 10))
        >>> pen._commands
        ['M10 10']
        # vertical line
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((10, 10))
        >>> pen.lineTo((10, 0))
        >>> pen._commands
        ['M10 10', 'V0']
        # horizontal line
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((10, 10))
        >>> pen.lineTo((0, 10))
        >>> pen._commands
        ['M10 10', 'H0']
        # basic
        >>> pen = SVGPathPen(None)
        >>> pen.lineTo((70, 80))
        >>> pen._commands
        ['L70 80']
        # basic following a moveto
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((0, 0))
        >>> pen.lineTo((10, 10))
        >>> pen._commands
        ['M0 0', ' 10 10']
        """
        x, y = pt
        # duplicate point
        if x == self._lastX and y == self._lastY:
            return
        # vertical line
        elif x == self._lastX:
            cmd = "V"
            pts = str(y)
        # horizontal line
        elif y == self._lastY:
            cmd = "H"
            pts = str(x)
        # previous was a moveto
        elif self._lastCommand == "M":
            cmd = None
            pts = " " + pointToString(pt)
        # basic
        else:
            cmd = "L"
            pts = pointToString(pt)
        # write the string
        t = ""
        if cmd:
            t += cmd
            self._lastCommand = cmd
        t += pts
        self._commands.append(t)
        # store for future reference
        self._lastX, self._lastY = pt

    def _curveToOne(self, pt1, pt2, pt3):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.curveTo((10, 20), (30, 40), (50, 60))
        >>> pen._commands
        ['C10 20 30 40 50 60']
        """
        t = "C"
        t += pointToString(pt1) + " "
        t += pointToString(pt2) + " "
        t += pointToString(pt3)
        self._commands.append(t)
        self._lastCommand = "C"
        self._lastX, self._lastY = pt3

    def _qCurveToOne(self, pt1, pt2):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.qCurveTo((10, 20), (30, 40))
        >>> pen._commands
        ['Q10 20 30 40']
        """
        assert pt2 is not None
        t = "Q"
        t += pointToString(pt1) + " "
        t += pointToString(pt2)
        self._commands.append(t)
        self._lastCommand = "Q"
        self._lastX, self._lastY = pt2

    def _closePath(self):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.closePath()
        >>> pen._commands
        ['Z']
        """
        self._commands.append("Z")
        self._lastCommand = "Z"
        self._lastX = self._lastY = None

    def _endPath(self):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.endPath()
        >>> pen._commands
        ['Z']
        """
        self._closePath()
        self._lastCommand = None
        self._lastX = self._lastY = None

    def getCommands(self):
        return "".join(self._commands)


class SVGPen(DrawablePenMixin, SVGPathPen):
    def __init__(self, dat, h):
        super().__init__(None)
        self.defs = []
        self.uses = []
        self.dat = dat
        self.h = h
        tp = TransformPen(self, (1, 0, 0, -1, 0, h))
        dat.round_to(0.1).replay(tp)
    
    def _endPath(self):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.endPath()
        >>> pen._commands
        ['Z']
        """
        #self._closePath()
        self._lastCommand = None
        self._lastX = self._lastY = None
    
    def fill(self, color):
        if color:
            if isinstance(color, Gradient):
                self.path.set("fill", f"url('#{self.gradient(color)}')")
            elif isinstance(color, Color):
                self.path.set("fill", self.rgba(color))
        else:
            self.path.set("fill", "transparent")
    
    def stroke(self, weight=1, color=None, dash=None):
        self.path.set("stroke-width", str(weight))
        if dash:
            self.path.set("stroke-dasharray", " ".join([str(x) for x in dash]))
        if color:
            if isinstance(color, Gradient):
                self.path.set("stroke", f"url('#{self.gradient(color)}')")
            elif isinstance(color, Color):
                self.path.set("stroke", self.rgba(color))
        else:
            self.path.set("stroke-width", 0)
            self.path.set("stroke", "transparent")
    
    def rgba(self, color):
        r, g, b, a = color.ints()
        return f"rgba({r}, {g}, {b}, {a})"
    
    def rect(self, rect):
        r = etree.Element("rect")
        fr = rect.flip(self.h)
        r.set("x", str(fr.x))
        r.set("y", str(fr.y))
        r.set("width", str(fr.w))
        r.set("height", str(fr.h))
        return r
    
    def shadow(self, clip=None, radius=10, alpha=0.3, color=Color.from_rgb(0,0,0,1)):
        hsh = str(hash(self.getCommands())) + str(randint(0, 1000000))
        f = etree.Element("filter")
        f.set("x", "0")
        f.set("y", "0")
        f.set("width", "1000%")
        f.set("height", "1000%")
        f.set("x", "-500%")
        f.set("y", "-500%")
        f.set("id", f"shadow-{hsh}")
        fe = etree.Element("feDropShadow")
        fe.set("dx", "0")
        fe.set("dy", "0")
        fe.set("stdDeviation", str(radius))
        #fe.set("slope", str(alpha))
        fe.set("flood-color", self.rgba(color))
        fe.set("flood-opacity", str(alpha))
        f.append(fe)
        self.defs.append(f)
        if clip:
            cp = etree.Element("clipPath")
            cp.set("id", f"clip-path_{hsh}")
            cp.append(self.rect(clip))
            self.defs.append(cp)
        #self.path.set("fill", "rgba(0, 0, 0, 0.3)")
        self.path.set("filter", f"url(#{f.get('id')})")
        if clip:
            self.path.set("clip-path", f"url(#clip-path_{hsh})")

    def gradient(self, gradient):
        lg = etree.Element("linearGradient")
        lg.set("id", f"gradient-{hash(self.getCommands())}-{randint(0, 100000)}")
        if gradient.stops[1][1].x == gradient.stops[0][1].x:
            lg.set("gradientTransform", "rotate(90)")
        s1 = etree.Element("stop", offset="0%")
        s1.set("stop-color", self.rgba(gradient.stops[0][0]))
        s2 = etree.Element("stop", offset="100%")
        s2.set("stop-color", self.rgba(gradient.stops[1][0]))
        lg.append(s1)
        lg.append(s2)
        self.defs.append(lg)
        return lg.get("id")
    
    def image(self, src=None, opacity=None, rect=None):
        if True:
            src = base64.b64encode(open(src, "rb").read()).decode('utf-8')
        hsh = str(hash(self.getCommands())) + str(randint(0, 100000))
        img = etree.Element("image")
        img.set("x", str(rect.x or 0))
        img.set("y", str(rect.y or 0))
        img.set("width", str(rect.w or 100))
        img.set("height", str(rect.h or 100))
        img.set("opacity", str(opacity))
        img.set("image-href", f"data:image/png;base64,{src}")
        pattern = etree.Element("pattern")
        pattern.set("x", img.get("x"))
        pattern.set("y", img.get("y"))
        pattern.set("width", img.get("width"))
        pattern.set("height", img.get("height"))
        pattern.set("patternUnits", "userSpaceOnUse")
        pattern.set("id", f"pattern-{hsh}")
        pattern.append(img)
        self.defs.append(pattern)
        self.path.set("fill", f"url(#pattern-{hsh})")
    
    def asSVG(self, style=None):
        self.path = etree.Element("path")
        for attrs, attr in self.findStyledAttrs(style):
            self.applyDATAttribute(attrs, attr)
        self.path.set("d", self.getCommands())
        tag = self.dat.tag()
        if tag:
            self.path.set("data-tag", tag)
        g = etree.Element("g")
        defs = etree.Element("defs")
        for d in self.defs:
            defs.append(d)
        g.append(defs)
        g.append(self.path)
        for u in self.uses:
            g.append(u)
        return g
    
    def Composite(pens, rect, offset=False, style=None, viewBox=False):
        docroot = etree.Element("svg")
        docroot.set("xmlns", "http://www.w3.org/2000/svg")
        if not viewBox:
            docroot.set("width", str(rect.w))
            docroot.set("height", str(rect.h))
        else:
            docroot.set("viewBox", f"0 0 {rect.w} {rect.h}")
            docroot.set("width", "100%")
        if offset:
            docroot.set("style", f"left:{rect.x}px;bottom:{rect.y}px;")
        
        for pen in SVGPen.FindPens(pens):
            sp = SVGPen(pen, rect.h)
            docroot.append(sp.asSVG(style=style))
        
        return etree.tostring(docroot, pretty_print=True).decode("utf-8").replace("image-href", "xlink:href")