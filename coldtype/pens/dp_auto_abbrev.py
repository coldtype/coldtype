from coldtype.geometry import Rect, Edge

def addComponent(glyphName, transformation):
	return ['addComponent', glyphName, transformation]

def øaddComponent(glyphName, transformation):
	return ['skip']

def skip_addComponent(glyphName, transformation):
	return ['skip']

def addFrame(frame, typographic=False):
	return ['addFrame', frame, typographic]

def øaddFrame(frame, typographic=False):
	return ['skip']

def skip_addFrame(frame, typographic=False):
	return ['skip']

def addSmoothPoints(length=100):
	return ['addSmoothPoints', length]

def øaddSmoothPoints(length=100):
	return ['skip']

def skip_addSmoothPoints(length=100):
	return ['skip']

def align(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return ['align', rect, x, y, th, tv, transformFrame]

def øalign(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return ['skip']

def skip_align(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return ['skip']

def allStyledAttrs(style=None):
	return ['allStyledAttrs', style]

def øallStyledAttrs(style=None):
	return ['skip']

def skip_allStyledAttrs(style=None):
	return ['skip']

def all_pens():
	return ['all_pens', ]

def øall_pens():
	return ['skip']

def skip_all_pens():
	return ['skip']

def attr(tag="default", field=None, **kwargs):
	return ['attr', tag, field, kwargs]

def øattr(tag="default", field=None, **kwargs):
	return ['skip']

def skip_attr(tag="default", field=None, **kwargs):
	return ['skip']

def bend(curve):
	return ['bend', curve]

def øbend(curve):
	return ['skip']

def skip_bend(curve):
	return ['skip']

def bounds():
	return ['bounds', ]

def øbounds():
	return ['skip']

def skip_bounds():
	return ['skip']

def bp():
	return ['bp', ]

def øbp():
	return ['skip']

def skip_bp():
	return ['skip']

def cast(_class, *args):
	return ['cast', _class, args]

def øcast(_class, *args):
	return ['skip']

def skip_cast(_class, *args):
	return ['skip']

def castshadow(angle=-45, width=100, ro=1, fill=1):
	return ['castshadow', angle, width, ro, fill]

def øcastshadow(angle=-45, width=100, ro=1, fill=1):
	return ['skip']

def skip_castshadow(angle=-45, width=100, ro=1, fill=1):
	return ['skip']

def catmull(points, close=False):
	return ['catmull', points, close]

def øcatmull(points, close=False):
	return ['skip']

def skip_catmull(points, close=False):
	return ['skip']

def circle(r, ext):
	return ['circle', r, ext]

def øcircle(r, ext):
	return ['skip']

def skip_circle(r, ext):
	return ['skip']

def clearAttrs():
	return ['clearAttrs', ]

def øclearAttrs():
	return ['skip']

def skip_clearAttrs():
	return ['skip']

def clearFrame():
	return ['clearFrame', ]

def øclearFrame():
	return ['skip']

def skip_clearFrame():
	return ['skip']

def closePath():
	return ['closePath', ]

def øclosePath():
	return ['skip']

def skip_closePath():
	return ['skip']

def contain(rect):
	return ['contain', rect]

def øcontain(rect):
	return ['skip']

def skip_contain(rect):
	return ['skip']

def copy():
	return ['copy', ]

def øcopy():
	return ['skip']

def skip_copy():
	return ['skip']

def curveTo(points):
	return ['curveTo', points]

def øcurveTo(points):
	return ['skip']

def skip_curveTo(points):
	return ['skip']

def db_drawPath(rect=None, filters=[]):
	return ['db_drawPath', rect, filters]

def ødb_drawPath(rect=None, filters=[]):
	return ['skip']

def skip_db_drawPath(rect=None, filters=[]):
	return ['skip']

def difference(otherPen):
	return ['difference', otherPen]

def ødifference(otherPen):
	return ['skip']

def skip_difference(otherPen):
	return ['skip']

def dots(radius=4):
	return ['dots', radius]

def ødots(radius=4):
	return ['skip']

def skip_dots(radius=4):
	return ['skip']

def endPath():
	return ['endPath', ]

def øendPath():
	return ['skip']

def skip_endPath():
	return ['skip']

def explode(into_set=False):
	return ['explode', into_set]

def øexplode(into_set=False):
	return ['skip']

def skip_explode(into_set=False):
	return ['skip']

def f(value):
	return ['f', value]

def øf(value):
	return ['skip']

def skip_f(value):
	return ['skip']

def fill(value):
	return ['fill', value]

def øfill(value):
	return ['skip']

def skip_fill(value):
	return ['skip']

def filmjitter(doneness, base=0, speed=(10, 20), scale=(2, 3), octaves=16):
	return ['filmjitter', doneness, base, speed, scale, octaves]

def øfilmjitter(doneness, base=0, speed=(10, 20), scale=(2, 3), octaves=16):
	return ['skip']

def skip_filmjitter(doneness, base=0, speed=(10, 20), scale=(2, 3), octaves=16):
	return ['skip']

def flatpoints():
	return ['flatpoints', ]

def øflatpoints():
	return ['skip']

def skip_flatpoints():
	return ['skip']

def flatten(length=10):
	return ['flatten', length]

def øflatten(length=10):
	return ['skip']

def skip_flatten(length=10):
	return ['skip']

def frameSet(th=False, tv=False):
	return ['frameSet', th, tv]

def øframeSet(th=False, tv=False):
	return ['skip']

def skip_frameSet(th=False, tv=False):
	return ['skip']

def getFrame(th=False, tv=False):
	return ['getFrame', th, tv]

def øgetFrame(th=False, tv=False):
	return ['skip']

def skip_getFrame(th=False, tv=False):
	return ['skip']

def getTag():
	return ['getTag', ]

def øgetTag():
	return ['skip']

def skip_getTag():
	return ['skip']

def glyph(glyph):
	return ['glyph', glyph]

def øglyph(glyph):
	return ['skip']

def skip_glyph(glyph):
	return ['skip']

def gridlines(rect, x=20, y=None):
	return ['gridlines', rect, x, y]

def øgridlines(rect, x=20, y=None):
	return ['skip']

def skip_gridlines(rect, x=20, y=None):
	return ['skip']

def grow(outline=10):
	return ['grow', outline]

def øgrow(outline=10):
	return ['skip']

def skip_grow(outline=10):
	return ['skip']

def hull(points):
	return ['hull', points]

def øhull(points):
	return ['skip']

def skip_hull(points):
	return ['skip']

def intersection(otherPen):
	return ['intersection', otherPen]

def øintersection(otherPen):
	return ['skip']

def skip_intersection(otherPen):
	return ['skip']

def line(points):
	return ['line', points]

def øline(points):
	return ['skip']

def skip_line(points):
	return ['skip']

def lineTo(p1):
	return ['lineTo', p1]

def ølineTo(p1):
	return ['skip']

def skip_lineTo(p1):
	return ['skip']

def lines():
	return ['lines', ]

def ølines():
	return ['skip']

def skip_lines():
	return ['skip']

def map(fn):
	return ['map', fn]

def ømap(fn):
	return ['skip']

def skip_map(fn):
	return ['skip']

def map_points(fn):
	return ['map_points', fn]

def ømap_points(fn):
	return ['skip']

def skip_map_points(fn):
	return ['skip']

def mod_contour(contour_index, mod_fn):
	return ['mod_contour', contour_index, mod_fn]

def ømod_contour(contour_index, mod_fn):
	return ['skip']

def skip_mod_contour(contour_index, mod_fn):
	return ['skip']

def moveTo(p0):
	return ['moveTo', p0]

def ømoveTo(p0):
	return ['skip']

def skip_moveTo(p0):
	return ['skip']

def nlt(fn):
	return ['nlt', fn]

def ønlt(fn):
	return ['skip']

def skip_nlt(fn):
	return ['skip']

def nonlinear_transform(fn):
	return ['nonlinear_transform', fn]

def ønonlinear_transform(fn):
	return ['skip']

def skip_nonlinear_transform(fn):
	return ['skip']

def noop(*args, **kwargs):
	return ['noop', args, kwargs]

def ønoop(*args, **kwargs):
	return ['skip']

def skip_noop(*args, **kwargs):
	return ['skip']

def nudge(lookup):
	return ['nudge', lookup]

def ønudge(lookup):
	return ['skip']

def skip_nudge(lookup):
	return ['skip']

def openAndClosed():
	return ['openAndClosed', ]

def øopenAndClosed():
	return ['skip']

def skip_openAndClosed():
	return ['skip']

def outline(offset=1, drawInner=True, drawOuter=True, cap="square"):
	return ['outline', offset, drawInner, drawOuter, cap]

def øoutline(offset=1, drawInner=True, drawOuter=True, cap="square"):
	return ['skip']

def skip_outline(offset=1, drawInner=True, drawOuter=True, cap="square"):
	return ['skip']

def oval(rect):
	return ['oval', rect]

def øoval(rect):
	return ['skip']

def skip_oval(rect):
	return ['skip']

def pattern(rect, clip=False):
	return ['pattern', rect, clip]

def øpattern(rect, clip=False):
	return ['skip']

def skip_pattern(rect, clip=False):
	return ['skip']

def pen():
	return ['pen', ]

def øpen():
	return ['skip']

def skip_pen():
	return ['skip']

def pixellate(rect, increment=50, inset=0):
	return ['pixellate', rect, increment, inset]

def øpixellate(rect, increment=50, inset=0):
	return ['skip']

def skip_pixellate(rect, increment=50, inset=0):
	return ['skip']

def point_t(t=0.5):
	return ['point_t', t]

def øpoint_t(t=0.5):
	return ['skip']

def skip_point_t(t=0.5):
	return ['skip']

def points():
	return ['points', ]

def øpoints():
	return ['skip']

def skip_points():
	return ['skip']

def polygon(sides, rect):
	return ['polygon', sides, rect]

def øpolygon(sides, rect):
	return ['skip']

def skip_polygon(sides, rect):
	return ['skip']

def potrace(pen_class, rect, poargs=[], invert=True):
	return ['potrace', pen_class, rect, poargs, invert]

def øpotrace(pen_class, rect, poargs=[], invert=True):
	return ['skip']

def skip_potrace(pen_class, rect, poargs=[], invert=True):
	return ['skip']

def precompose(pen_class, rect):
	return ['precompose', pen_class, rect]

def øprecompose(pen_class, rect):
	return ['skip']

def skip_precompose(pen_class, rect):
	return ['skip']

def project(angle, width):
	return ['project', angle, width]

def øproject(angle, width):
	return ['skip']

def skip_project(angle, width):
	return ['skip']

def qCurveTo(points):
	return ['qCurveTo', points]

def øqCurveTo(points):
	return ['skip']

def skip_qCurveTo(points):
	return ['skip']

def quadratic(a, b, c, lineTo=False):
	return ['quadratic', a, b, c, lineTo]

def øquadratic(a, b, c, lineTo=False):
	return ['skip']

def skip_quadratic(a, b, c, lineTo=False):
	return ['skip']

def record(pen):
	return ['record', pen]

def ørecord(pen):
	return ['skip']

def skip_record(pen):
	return ['skip']

def rect(rect, *args):
	return ['rect', rect, args]

def ørect(rect, *args):
	return ['skip']

def skip_rect(rect, *args):
	return ['skip']

def removeBlanks():
	return ['removeBlanks', ]

def øremoveBlanks():
	return ['skip']

def skip_removeBlanks():
	return ['skip']

def removeOverlap():
	return ['removeOverlap', ]

def øremoveOverlap():
	return ['skip']

def skip_removeOverlap():
	return ['skip']

def repeat(times=1):
	return ['repeat', times]

def ørepeat(times=1):
	return ['skip']

def skip_repeat(times=1):
	return ['skip']

def repeatx(times=1):
	return ['repeatx', times]

def ørepeatx(times=1):
	return ['skip']

def skip_repeatx(times=1):
	return ['skip']

def replay(pen):
	return ['replay', pen]

def øreplay(pen):
	return ['skip']

def skip_replay(pen):
	return ['skip']

def reverse():
	return ['reverse', ]

def øreverse():
	return ['skip']

def skip_reverse():
	return ['skip']

def reverseDifference(otherPen):
	return ['reverseDifference', otherPen]

def øreverseDifference(otherPen):
	return ['skip']

def skip_reverseDifference(otherPen):
	return ['skip']

def rotate(degrees, point=None):
	return ['rotate', degrees, point]

def ørotate(degrees, point=None):
	return ['skip']

def skip_rotate(degrees, point=None):
	return ['skip']

def roughen(amplitude=10, threshold=10):
	return ['roughen', amplitude, threshold]

def øroughen(amplitude=10, threshold=10):
	return ['skip']

def skip_roughen(amplitude=10, threshold=10):
	return ['skip']

def round(rounding):
	return ['round', rounding]

def øround(rounding):
	return ['skip']

def skip_round(rounding):
	return ['skip']

def roundedRect(rect, hr, vr):
	return ['roundedRect', rect, hr, vr]

def øroundedRect(rect, hr, vr):
	return ['skip']

def skip_roundedRect(rect, hr, vr):
	return ['skip']

def s(value):
	return ['s', value]

def øs(value):
	return ['skip']

def skip_s(value):
	return ['skip']

def scale(scaleX, scaleY=None, center=None):
	return ['scale', scaleX, scaleY, center]

def øscale(scaleX, scaleY=None, center=None):
	return ['skip']

def skip_scale(scaleX, scaleY=None, center=None):
	return ['skip']

def scaleToHeight(h):
	return ['scaleToHeight', h]

def øscaleToHeight(h):
	return ['skip']

def skip_scaleToHeight(h):
	return ['skip']

def scaleToRect(rect, preserveAspect=True):
	return ['scaleToRect', rect, preserveAspect]

def øscaleToRect(rect, preserveAspect=True):
	return ['skip']

def skip_scaleToRect(rect, preserveAspect=True):
	return ['skip']

def scaleToWidth(w):
	return ['scaleToWidth', w]

def øscaleToWidth(w):
	return ['skip']

def skip_scaleToWidth(w):
	return ['skip']

def scanlines(rect, sample=40, width=20, threshold=10):
	return ['scanlines', rect, sample, width, threshold]

def øscanlines(rect, sample=40, width=20, threshold=10):
	return ['skip']

def skip_scanlines(rect, sample=40, width=20, threshold=10):
	return ['skip']

def semicircle(r, center, fext=0.5, rext=0.5):
	return ['semicircle', r, center, fext, rext]

def øsemicircle(r, center, fext=0.5, rext=0.5):
	return ['skip']

def skip_semicircle(r, center, fext=0.5, rext=0.5):
	return ['skip']

def simplify():
	return ['simplify', ]

def øsimplify():
	return ['skip']

def skip_simplify():
	return ['skip']

def sine(r, periods):
	return ['sine', r, periods]

def øsine(r, periods):
	return ['skip']

def skip_sine(r, periods):
	return ['skip']

def skeleton(scale=1, returnSet=False):
	return ['skeleton', scale, returnSet]

def øskeleton(scale=1, returnSet=False):
	return ['skip']

def skip_skeleton(scale=1, returnSet=False):
	return ['skip']

def skeletonPoints():
	return ['skeletonPoints', ]

def øskeletonPoints():
	return ['skip']

def skip_skeletonPoints():
	return ['skip']

def skew(x=0, y=0, point=None):
	return ['skew', x, y, point]

def øskew(x=0, y=0, point=None):
	return ['skip']

def skip_skew(x=0, y=0, point=None):
	return ['skip']

def slicec(contour_slice):
	return ['slicec', contour_slice]

def øslicec(contour_slice):
	return ['skip']

def skip_slicec(contour_slice):
	return ['skip']

def smooth():
	return ['smooth', ]

def øsmooth():
	return ['skip']

def skip_smooth():
	return ['skip']

def standingwave(r, periods, direction=1):
	return ['standingwave', r, periods, direction]

def østandingwave(r, periods, direction=1):
	return ['skip']

def skip_standingwave(r, periods, direction=1):
	return ['skip']

def stroke(value):
	return ['stroke', value]

def østroke(value):
	return ['skip']

def skip_stroke(value):
	return ['skip']

def strokeWidth(value):
	return ['strokeWidth', value]

def østrokeWidth(value):
	return ['skip']

def skip_strokeWidth(value):
	return ['skip']

def subsegment(start=0, end=1):
	return ['subsegment', start, end]

def øsubsegment(start=0, end=1):
	return ['skip']

def skip_subsegment(start=0, end=1):
	return ['skip']

def svg(file, gid, rect=Rect([0, 0, 0, 100])):
	return ['svg', file, gid, rect]

def øsvg(file, gid, rect=Rect([0, 0, 0, 100])):
	return ['skip']

def skip_svg(file, gid, rect=Rect([0, 0, 0, 100])):
	return ['skip']

def sw(value):
	return ['sw', value]

def øsw(value):
	return ['skip']

def skip_sw(value):
	return ['skip']

def tag(tag):
	return ['tag', tag]

def øtag(tag):
	return ['skip']

def skip_tag(tag):
	return ['skip']

def take(slice):
	return ['take', slice]

def øtake(slice):
	return ['skip']

def skip_take(slice):
	return ['skip']

def to_glyph(name=None, width=None):
	return ['to_glyph', name, width]

def øto_glyph(name=None, width=None):
	return ['skip']

def skip_to_glyph(name=None, width=None):
	return ['skip']

def trackToRect(rect, pullToEdges=False, r=0):
	return ['trackToRect', rect, pullToEdges, r]

def øtrackToRect(rect, pullToEdges=False, r=0):
	return ['skip']

def skip_trackToRect(rect, pullToEdges=False, r=0):
	return ['skip']

def transform(transform, transformFrame=True):
	return ['transform', transform, transformFrame]

def øtransform(transform, transformFrame=True):
	return ['skip']

def skip_transform(transform, transformFrame=True):
	return ['skip']

def translate(x, y=None, transformFrame=True):
	return ['translate', x, y, transformFrame]

def øtranslate(x, y=None, transformFrame=True):
	return ['skip']

def skip_translate(x, y=None, transformFrame=True):
	return ['skip']

def union(otherPen):
	return ['union', otherPen]

def øunion(otherPen):
	return ['skip']

def skip_union(otherPen):
	return ['skip']

def ups():
	return ['ups', ]

def øups():
	return ['skip']

def skip_ups():
	return ['skip']

def vl(value):
	return ['vl', value]

def øvl(value):
	return ['skip']

def skip_vl(value):
	return ['skip']

def walk(callback, depth=0):
	return ['walk', callback, depth]

def øwalk(callback, depth=0):
	return ['skip']

def skip_walk(callback, depth=0):
	return ['skip']

def xAlignToFrame(x=Edge.CenterX, th=0):
	return ['xAlignToFrame', x, th]

def øxAlignToFrame(x=Edge.CenterX, th=0):
	return ['skip']

def skip_xAlignToFrame(x=Edge.CenterX, th=0):
	return ['skip']

def xor(otherPen):
	return ['xor', otherPen]

def øxor(otherPen):
	return ['skip']

def skip_xor(otherPen):
	return ['skip']

def å(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return ['å', rect, x, y, th, tv, transformFrame]

def øå(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return ['skip']

def skip_å(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return ['skip']

