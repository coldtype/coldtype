from coldtype.geometry import Rect, Edge
from coldtype.abbr.inst import Inst

def addComponent(glyphName, transformation):
	return Inst('addComponent', glyphName, transformation)

def addFrame(frame, typographic=False, passthru=False):
	return Inst('addFrame', frame, typographic, passthru)

def addSmoothPoints(length=100):
	return Inst('addSmoothPoints', length)

def align(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return Inst('align', rect, x, y, th, tv, transformFrame)

def allStyledAttrs(style=None):
	return Inst('allStyledAttrs', style)

def all_pens():
	return Inst('all_pens', )

def attr(tag="default", field=None, **kwargs):
	return Inst('attr', tag, field, kwargs)

def bend(curve):
	return Inst('bend', curve)

def bounds():
	return Inst('bounds', )

def bp():
	return Inst('bp', )

def cast(_class, *args):
	return Inst('cast', _class, args)

def castshadow(angle=-45, width=100, ro=1, fill=1):
	return Inst('castshadow', angle, width, ro, fill)

def catmull(points, close=False):
	return Inst('catmull', points, close)

def circle(r, ext):
	return Inst('circle', r, ext)

def clearAttrs():
	return Inst('clearAttrs', )

def clearFrame():
	return Inst('clearFrame', )

def closePath():
	return Inst('closePath', )

def contain(rect):
	return Inst('contain', rect)

def copy():
	return Inst('copy', )

def curveTo(points):
	return Inst('curveTo', points)

def db_drawPath(rect=None, filters=[]):
	return Inst('db_drawPath', rect, filters)

def difference(otherPen):
	return Inst('difference', otherPen)

def dots(radius=4):
	return Inst('dots', radius)

def endPath():
	return Inst('endPath', )

def explode(into_set=False):
	return Inst('explode', into_set)

def f(value):
	return Inst('f', value)

def fill(value):
	return Inst('fill', value)

def filmjitter(doneness, base=0, speed=(10, 20), scale=(2, 3), octaves=16):
	return Inst('filmjitter', doneness, base, speed, scale, octaves)

def filter_contours(filter_fn):
	return Inst('filter_contours', filter_fn)

def flatpoints():
	return Inst('flatpoints', )

def flatten(length=10):
	return Inst('flatten', length)

def frameSet(th=False, tv=False):
	return Inst('frameSet', th, tv)

def getFrame(th=False, tv=False):
	return Inst('getFrame', th, tv)

def getTag():
	return Inst('getTag', )

def glyph(glyph):
	return Inst('glyph', glyph)

def gridlines(rect, x=20, y=None):
	return Inst('gridlines', rect, x, y)

def grow(outline=10):
	return Inst('grow', outline)

def hull(points):
	return Inst('hull', points)

def intersection(otherPen):
	return Inst('intersection', otherPen)

def line(points):
	return Inst('line', points)

def lineTo(p1):
	return Inst('lineTo', p1)

def lines():
	return Inst('lines', )

def map(fn):
	return Inst('map', fn)

def map_points(fn):
	return Inst('map_points', fn)

def mod_contour(contour_index, mod_fn):
	return Inst('mod_contour', contour_index, mod_fn)

def moveTo(p0):
	return Inst('moveTo', p0)

def nlt(fn):
	return Inst('nlt', fn)

def nonlinear_transform(fn):
	return Inst('nonlinear_transform', fn)

def noop(*args, **kwargs):
	return Inst('noop', args, kwargs)

def nudge(lookup):
	return Inst('nudge', lookup)

def openAndClosed():
	return Inst('openAndClosed', )

def outline(offset=1, drawInner=True, drawOuter=True, cap="square"):
	return Inst('outline', offset, drawInner, drawOuter, cap)

def oval(rect):
	return Inst('oval', rect)

def pattern(rect, clip=False):
	return Inst('pattern', rect, clip)

def pen():
	return Inst('pen', )

def pixellate(rect, increment=50, inset=0):
	return Inst('pixellate', rect, increment, inset)

def point_t(t=0.5):
	return Inst('point_t', t)

def points():
	return Inst('points', )

def polygon(sides, rect):
	return Inst('polygon', sides, rect)

def potrace(pen_class, rect, poargs=[], invert=True, context=None):
	return Inst('potrace', pen_class, rect, poargs, invert, context)

def precompose(pen_class, rect, context=None):
	return Inst('precompose', pen_class, rect, context)

def project(angle, width):
	return Inst('project', angle, width)

def qCurveTo(points):
	return Inst('qCurveTo', points)

def quadratic(a, b, c, lineTo=False):
	return Inst('quadratic', a, b, c, lineTo)

def rasterized(pen_class, rect, context=None):
	return Inst('rasterized', pen_class, rect, context)

def record(pen):
	return Inst('record', pen)

def rect(rect, *args):
	return Inst('rect', rect, args)

def removeBlanks():
	return Inst('removeBlanks', )

def removeOverlap():
	return Inst('removeOverlap', )

def repeat(times=1):
	return Inst('repeat', times)

def repeatx(times=1):
	return Inst('repeatx', times)

def replay(pen):
	return Inst('replay', pen)

def reverse():
	return Inst('reverse', )

def reverseDifference(otherPen):
	return Inst('reverseDifference', otherPen)

def rotate(degrees, point=None):
	return Inst('rotate', degrees, point)

def roughen(amplitude=10, threshold=10):
	return Inst('roughen', amplitude, threshold)

def round(rounding):
	return Inst('round', rounding)

def roundedRect(rect, hr, vr):
	return Inst('roundedRect', rect, hr, vr)

def s(value):
	return Inst('s', value)

def scale(scaleX, scaleY=None, center=None):
	return Inst('scale', scaleX, scaleY, center)

def scaleToHeight(h):
	return Inst('scaleToHeight', h)

def scaleToRect(rect, preserveAspect=True):
	return Inst('scaleToRect', rect, preserveAspect)

def scaleToWidth(w):
	return Inst('scaleToWidth', w)

def scanlines(rect, sample=40, width=20, threshold=10):
	return Inst('scanlines', rect, sample, width, threshold)

def semicircle(r, center, fext=0.5, rext=0.5):
	return Inst('semicircle', r, center, fext, rext)

def simplify():
	return Inst('simplify', )

def sine(r, periods):
	return Inst('sine', r, periods)

def skeleton(scale=1, returnSet=False):
	return Inst('skeleton', scale, returnSet)

def skeletonPoints():
	return Inst('skeletonPoints', )

def skew(x=0, y=0, point=None):
	return Inst('skew', x, y, point)

def slicec(contour_slice):
	return Inst('slicec', contour_slice)

def smooth():
	return Inst('smooth', )

def standingwave(r, periods, direction=1):
	return Inst('standingwave', r, periods, direction)

def stroke(value):
	return Inst('stroke', value)

def strokeWidth(value):
	return Inst('strokeWidth', value)

def subsegment(start=0, end=1):
	return Inst('subsegment', start, end)

def svg(file, gid, rect=Rect([0, 0, 0, 100])):
	return Inst('svg', file, gid, rect)

def sw(value):
	return Inst('sw', value)

def tag(tag):
	return Inst('tag', tag)

def take(slice):
	return Inst('take', slice)

def to_glyph(name=None, width=None):
	return Inst('to_glyph', name, width)

def to_pen():
	return Inst('to_pen', )

def trackToRect(rect, pullToEdges=False, r=0):
	return Inst('trackToRect', rect, pullToEdges, r)

def transform(transform, transformFrame=True):
	return Inst('transform', transform, transformFrame)

def translate(x, y=None, transformFrame=True):
	return Inst('translate', x, y, transformFrame)

def union(otherPen):
	return Inst('union', otherPen)

def ups():
	return Inst('ups', )

def vl(value):
	return Inst('vl', value)

def walk(callback, depth=0):
	return Inst('walk', callback, depth)

def xAlignToFrame(x=Edge.CenterX, th=0):
	return Inst('xAlignToFrame', x, th)

def xor(otherPen):
	return Inst('xor', otherPen)

def å(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return Inst('å', rect, x, y, th, tv, transformFrame)

def Glyphs(ufo, glyphNames):
	return Inst('Glyphs', ufo, glyphNames)

def addOverlaps(idx1, idx2, which, outline=3, scale=1, xray=0):
	return Inst('addOverlaps', idx1, idx2, which, outline, scale, xray)

def alignToRects(rects, x=Edge.CenterX, y=Edge.CenterY, th=1, tv=1):
	return Inst('alignToRects', rects, x, y, th, tv)

def append(pen, allow_blank=False):
	return Inst('append', pen, allow_blank)

def clearFrames():
	return Inst('clearFrames', )

def collapse(levels=100, onself=False):
	return Inst('collapse', levels, onself)

def collapseonce():
	return Inst('collapseonce', )

def distribute(v=False):
	return Inst('distribute', v)

def distributeOnPath(path, offset=0, cc=None, notfound=None):
	return Inst('distributeOnPath', path, offset, cc, notfound)

def extend(pens):
	return Inst('extend', pens)

def ffg(glyph_name):
	return Inst('ffg', glyph_name)

def fft(tag):
	return Inst('fft', tag)

def filter(fn):
	return Inst('filter', fn)

def glyphs_named(glyph_name):
	return Inst('glyphs_named', glyph_name)

def implode():
	return Inst('implode', )

def indexed_subset(indices):
	return Inst('indexed_subset', indices)

def insert(index, pen):
	return Inst('insert', index, pen)

def interleave(style_fn, direction=-1, recursive=True):
	return Inst('interleave', style_fn, direction, recursive)

def mfilter(fn):
	return Inst('mfilter', fn)

def mmap(fn):
	return Inst('mmap', fn)

def overlapPair(gn1, gn2, which, outline=3):
	return Inst('overlapPair', gn1, gn2, which, outline)

def overlapPairs(pairs, outline=3):
	return Inst('overlapPairs', pairs, outline)

def pfilter(fn):
	return Inst('pfilter', fn)

def pmap(fn):
	return Inst('pmap', fn)

def print_tree(depth=0):
	return Inst('print_tree', depth)

def reversePens():
	return Inst('reversePens', )

def rp():
	return Inst('rp', )

def tagged(tag):
	return Inst('tagged', tag)

def track(t, v=False):
	return Inst('track', t, v)

def understroke(s=0, sw=5, outline=False, dofill=0):
	return Inst('understroke', s, sw, outline, dofill)

