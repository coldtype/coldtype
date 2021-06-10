from fontTools.pens.basePen import BasePen

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import transparent

from coldtype.pens.dattext import DATText
from coldtype.geometry import Point
from coldtype.pens.drawablepen import DrawablePenMixin


class ReportLabPathPen(BasePen):
	def __init__(self, canvas):
		super().__init__()
		self.path = canvas.beginPath()

	def _moveTo(self, p):
		(x,y) = p
		self.path.moveTo(x,y)

	def _lineTo(self, p):
		(x,y) = p
		self.path.lineTo(x,y)

	def _curveToOne(self, p1, p2, p3):
		(x1,y1) = p1
		(x2,y2) = p2
		(x3,y3) = p3
		self.path.curveTo(x1, y1, x2, y2, x3, y3)

	def _closePath(self):
		self.path.close()


class ReportLabPen(DrawablePenMixin):
    def __init__(self, dat, rect, canvas, scale, style=None, alpha=1):
        super().__init__()
        self.dat = dat
        self.scale = scale
        self.canvas = canvas
        self.rect = rect
        self.style = style
        self.alpha = alpha
        
        rpp = ReportLabPathPen(canvas)
        dat.replay(rpp)
        self.path = rpp.path

        all_attrs = list(self.findStyledAttrs(style))

        canvas.saveState()
        for attrs, attr in all_attrs:
            method, *args = attr
            do_stroke = 0
            do_fill = 0
            if method == "stroke" and args[0].get("weight") != 0:
                do_stroke = 1
            elif method == "fill" and args[0].a > 0:
                do_fill = 1
            self.applyDATAttribute(attrs, attr)
            canvas.drawPath(self.path, fill=do_fill, stroke=do_stroke)
        canvas.restoreState()
    
    def fill(self, color):
        self.canvas.setFillColorRGB(color.r, color.g, color.b)
    
    def stroke(self, weight=1, color=None, dash=None):
        #return
        if weight == 0:
            self.canvas.setStrokeColor(transparent)
            self.canvas.setLineWidth(0)
            return
        self.canvas.setStrokeColorRGB(color.r, color.g, color.b)
        self.canvas.setLineWidth(weight)
    
    def PDF(pens, rect, save_to, scale=1, style=None, title=None):
        c = Canvas(save_to, pagesize=letter)
        ReportLabPen.CompositeToCanvas(pens, rect, c, scale=scale, style=style)
        if title:
            c.setTitle(title)
        c.showPage()
        c.save() # necessary?
    
    def CompositeToCanvas(pens, rect, canvas, scale=1, style=None):
        if scale != 1:
            pens.scale(scale, scale, Point((0, 0)))
        
        if not pens.visible:
            return
        
        def draw(pen, state, data):
            if state != 0 or not pen.visible:
                return
            
            if isinstance(pen, DATText):
                # TODO, look at SkiaPen for reference implementation
                return
            
            if state == 0:
                ReportLabPen(pen, rect, canvas, scale, style=style, alpha=data["alpha"])
        
        pens.walk(draw, visible_only=True)