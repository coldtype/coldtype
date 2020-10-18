from coldtype.geometry import Rect, Edge

def addComponent(glyphName, transformation):
	return ['addComponent', glyphName, transformation]

def øaddComponent(glyphName, transformation):
	return ['skip']

def s_addComponent(glyphName, transformation):
	return ['skip']

def addFrame(frame, typographic=False, passthru=False):
	return ['addFrame', frame, typographic, passthru]

def øaddFrame(frame, typographic=False, passthru=False):
	return ['skip']

def s_addFrame(frame, typographic=False, passthru=False):
	return ['skip']

def addSmoothPoints(length=100):
	return ['addSmoothPoints', length]

def øaddSmoothPoints(length=100):
	return ['skip']

def s_addSmoothPoints(length=100):
	return ['skip']

def align(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return ['align', rect, x, y, th, tv, transformFrame]

def øalign(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return ['skip']

def s_align(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return ['skip']

def allStyledAttrs(style=None):
	return ['allStyledAttrs', style]

def øallStyledAttrs(style=None):
	return ['skip']

def s_allStyledAttrs(style=None):
	return ['skip']

def all_pens():
	return ['all_pens', ]

def øall_pens():
	return ['skip']

def s_all_pens():
	return ['skip']

def attr(tag="default", field=None, **kwargs):
	return ['attr', tag, field, kwargs]

def øattr(tag="default", field=None, **kwargs):
	return ['skip']

def s_attr(tag="default", field=None, **kwargs):
	return ['skip']

def bend(curve):
	return ['bend', curve]

def øbend(curve):
	return ['skip']

def s_bend(curve):
	return ['skip']

def bounds():
	return ['bounds', ]

def øbounds():
	return ['skip']

def s_bounds():
	return ['skip']

def bp():
	return ['bp', ]

def øbp():
	return ['skip']

def s_bp():
	return ['skip']

def cast(_class, *args):
	return ['cast', _class, args]

def øcast(_class, *args):
	return ['skip']

def s_cast(_class, *args):
	return ['skip']

def castshadow(angle=-45, width=100, ro=1, fill=1):
	return ['castshadow', angle, width, ro, fill]

def øcastshadow(angle=-45, width=100, ro=1, fill=1):
	return ['skip']

def s_castshadow(angle=-45, width=100, ro=1, fill=1):
	return ['skip']

def catmull(points, close=False):
	return ['catmull', points, close]

def øcatmull(points, close=False):
	return ['skip']

def s_catmull(points, close=False):
	return ['skip']

def circle(r, ext):
	return ['circle', r, ext]

def øcircle(r, ext):
	return ['skip']

def s_circle(r, ext):
	return ['skip']

def clearAttrs():
	return ['clearAttrs', ]

def øclearAttrs():
	return ['skip']

def s_clearAttrs():
	return ['skip']

def clearFrame():
	return ['clearFrame', ]

def øclearFrame():
	return ['skip']

def s_clearFrame():
	return ['skip']

def closePath():
	return ['closePath', ]

def øclosePath():
	return ['skip']

def s_closePath():
	return ['skip']

def contain(rect):
	return ['contain', rect]

def øcontain(rect):
	return ['skip']

def s_contain(rect):
	return ['skip']

def copy():
	return ['copy', ]

def øcopy():
	return ['skip']

def s_copy():
	return ['skip']

def curveTo(points):
	return ['curveTo', points]

def øcurveTo(points):
	return ['skip']

def s_curveTo(points):
	return ['skip']

def db_drawPath(rect=None, filters=[]):
	return ['db_drawPath', rect, filters]

def ødb_drawPath(rect=None, filters=[]):
	return ['skip']

def s_db_drawPath(rect=None, filters=[]):
	return ['skip']

def difference(otherPen):
	return ['difference', otherPen]

def ødifference(otherPen):
	return ['skip']

def s_difference(otherPen):
	return ['skip']

def dots(radius=4):
	return ['dots', radius]

def ødots(radius=4):
	return ['skip']

def s_dots(radius=4):
	return ['skip']

def endPath():
	return ['endPath', ]

def øendPath():
	return ['skip']

def s_endPath():
	return ['skip']

def explode(into_set=False):
	return ['explode', into_set]

def øexplode(into_set=False):
	return ['skip']

def s_explode(into_set=False):
	return ['skip']

def f(value):
	return ['f', value]

def øf(value):
	return ['skip']

def s_f(value):
	return ['skip']

def fill(value):
	return ['fill', value]

def øfill(value):
	return ['skip']

def s_fill(value):
	return ['skip']

def filmjitter(doneness, base=0, speed=(10, 20), scale=(2, 3), octaves=16):
	return ['filmjitter', doneness, base, speed, scale, octaves]

def øfilmjitter(doneness, base=0, speed=(10, 20), scale=(2, 3), octaves=16):
	return ['skip']

def s_filmjitter(doneness, base=0, speed=(10, 20), scale=(2, 3), octaves=16):
	return ['skip']

def flatpoints():
	return ['flatpoints', ]

def øflatpoints():
	return ['skip']

def s_flatpoints():
	return ['skip']

def flatten(length=10):
	return ['flatten', length]

def øflatten(length=10):
	return ['skip']

def s_flatten(length=10):
	return ['skip']

def frameSet(th=False, tv=False):
	return ['frameSet', th, tv]

def øframeSet(th=False, tv=False):
	return ['skip']

def s_frameSet(th=False, tv=False):
	return ['skip']

def getFrame(th=False, tv=False):
	return ['getFrame', th, tv]

def øgetFrame(th=False, tv=False):
	return ['skip']

def s_getFrame(th=False, tv=False):
	return ['skip']

def getTag():
	return ['getTag', ]

def øgetTag():
	return ['skip']

def s_getTag():
	return ['skip']

def glyph(glyph):
	return ['glyph', glyph]

def øglyph(glyph):
	return ['skip']

def s_glyph(glyph):
	return ['skip']

def gridlines(rect, x=20, y=None):
	return ['gridlines', rect, x, y]

def øgridlines(rect, x=20, y=None):
	return ['skip']

def s_gridlines(rect, x=20, y=None):
	return ['skip']

def grow(outline=10):
	return ['grow', outline]

def øgrow(outline=10):
	return ['skip']

def s_grow(outline=10):
	return ['skip']

def hull(points):
	return ['hull', points]

def øhull(points):
	return ['skip']

def s_hull(points):
	return ['skip']

def intersection(otherPen):
	return ['intersection', otherPen]

def øintersection(otherPen):
	return ['skip']

def s_intersection(otherPen):
	return ['skip']

def line(points):
	return ['line', points]

def øline(points):
	return ['skip']

def s_line(points):
	return ['skip']

def lineTo(p1):
	return ['lineTo', p1]

def ølineTo(p1):
	return ['skip']

def s_lineTo(p1):
	return ['skip']

def lines():
	return ['lines', ]

def ølines():
	return ['skip']

def s_lines():
	return ['skip']

def map(fn):
	return ['map', fn]

def ømap(fn):
	return ['skip']

def s_map(fn):
	return ['skip']

def map_points(fn):
	return ['map_points', fn]

def ømap_points(fn):
	return ['skip']

def s_map_points(fn):
	return ['skip']

def mod_contour(contour_index, mod_fn):
	return ['mod_contour', contour_index, mod_fn]

def ømod_contour(contour_index, mod_fn):
	return ['skip']

def s_mod_contour(contour_index, mod_fn):
	return ['skip']

def moveTo(p0):
	return ['moveTo', p0]

def ømoveTo(p0):
	return ['skip']

def s_moveTo(p0):
	return ['skip']

def nlt(fn):
	return ['nlt', fn]

def ønlt(fn):
	return ['skip']

def s_nlt(fn):
	return ['skip']

def nonlinear_transform(fn):
	return ['nonlinear_transform', fn]

def ønonlinear_transform(fn):
	return ['skip']

def s_nonlinear_transform(fn):
	return ['skip']

def noop(*args, **kwargs):
	return ['noop', args, kwargs]

def ønoop(*args, **kwargs):
	return ['skip']

def s_noop(*args, **kwargs):
	return ['skip']

def nudge(lookup):
	return ['nudge', lookup]

def ønudge(lookup):
	return ['skip']

def s_nudge(lookup):
	return ['skip']

def openAndClosed():
	return ['openAndClosed', ]

def øopenAndClosed():
	return ['skip']

def s_openAndClosed():
	return ['skip']

def outline(offset=1, drawInner=True, drawOuter=True, cap="square"):
	return ['outline', offset, drawInner, drawOuter, cap]

def øoutline(offset=1, drawInner=True, drawOuter=True, cap="square"):
	return ['skip']

def s_outline(offset=1, drawInner=True, drawOuter=True, cap="square"):
	return ['skip']

def oval(rect):
	return ['oval', rect]

def øoval(rect):
	return ['skip']

def s_oval(rect):
	return ['skip']

def pattern(rect, clip=False):
	return ['pattern', rect, clip]

def øpattern(rect, clip=False):
	return ['skip']

def s_pattern(rect, clip=False):
	return ['skip']

def pen():
	return ['pen', ]

def øpen():
	return ['skip']

def s_pen():
	return ['skip']

def pixellate(rect, increment=50, inset=0):
	return ['pixellate', rect, increment, inset]

def øpixellate(rect, increment=50, inset=0):
	return ['skip']

def s_pixellate(rect, increment=50, inset=0):
	return ['skip']

def point_t(t=0.5):
	return ['point_t', t]

def øpoint_t(t=0.5):
	return ['skip']

def s_point_t(t=0.5):
	return ['skip']

def points():
	return ['points', ]

def øpoints():
	return ['skip']

def s_points():
	return ['skip']

def polygon(sides, rect):
	return ['polygon', sides, rect]

def øpolygon(sides, rect):
	return ['skip']

def s_polygon(sides, rect):
	return ['skip']

def potrace(pen_class, rect, poargs=[], invert=True, context=None):
	return ['potrace', pen_class, rect, poargs, invert, context]

def øpotrace(pen_class, rect, poargs=[], invert=True, context=None):
	return ['skip']

def s_potrace(pen_class, rect, poargs=[], invert=True, context=None):
	return ['skip']

def precompose(pen_class, rect, context=None):
	return ['precompose', pen_class, rect, context]

def øprecompose(pen_class, rect, context=None):
	return ['skip']

def s_precompose(pen_class, rect, context=None):
	return ['skip']

def project(angle, width):
	return ['project', angle, width]

def øproject(angle, width):
	return ['skip']

def s_project(angle, width):
	return ['skip']

def qCurveTo(points):
	return ['qCurveTo', points]

def øqCurveTo(points):
	return ['skip']

def s_qCurveTo(points):
	return ['skip']

def quadratic(a, b, c, lineTo=False):
	return ['quadratic', a, b, c, lineTo]

def øquadratic(a, b, c, lineTo=False):
	return ['skip']

def s_quadratic(a, b, c, lineTo=False):
	return ['skip']

def rasterized(pen_class, rect, context=None):
	return ['rasterized', pen_class, rect, context]

def ørasterized(pen_class, rect, context=None):
	return ['skip']

def s_rasterized(pen_class, rect, context=None):
	return ['skip']

def record(pen):
	return ['record', pen]

def ørecord(pen):
	return ['skip']

def s_record(pen):
	return ['skip']

def rect(rect, *args):
	return ['rect', rect, args]

def ørect(rect, *args):
	return ['skip']

def s_rect(rect, *args):
	return ['skip']

def removeBlanks():
	return ['removeBlanks', ]

def øremoveBlanks():
	return ['skip']

def s_removeBlanks():
	return ['skip']

def removeOverlap():
	return ['removeOverlap', ]

def øremoveOverlap():
	return ['skip']

def s_removeOverlap():
	return ['skip']

def repeat(times=1):
	return ['repeat', times]

def ørepeat(times=1):
	return ['skip']

def s_repeat(times=1):
	return ['skip']

def repeatx(times=1):
	return ['repeatx', times]

def ørepeatx(times=1):
	return ['skip']

def s_repeatx(times=1):
	return ['skip']

def replay(pen):
	return ['replay', pen]

def øreplay(pen):
	return ['skip']

def s_replay(pen):
	return ['skip']

def reverse():
	return ['reverse', ]

def øreverse():
	return ['skip']

def s_reverse():
	return ['skip']

def reverseDifference(otherPen):
	return ['reverseDifference', otherPen]

def øreverseDifference(otherPen):
	return ['skip']

def s_reverseDifference(otherPen):
	return ['skip']

def rotate(degrees, point=None):
	return ['rotate', degrees, point]

def ørotate(degrees, point=None):
	return ['skip']

def s_rotate(degrees, point=None):
	return ['skip']

def roughen(amplitude=10, threshold=10):
	return ['roughen', amplitude, threshold]

def øroughen(amplitude=10, threshold=10):
	return ['skip']

def s_roughen(amplitude=10, threshold=10):
	return ['skip']

def round(rounding):
	return ['round', rounding]

def øround(rounding):
	return ['skip']

def s_round(rounding):
	return ['skip']

def roundedRect(rect, hr, vr):
	return ['roundedRect', rect, hr, vr]

def øroundedRect(rect, hr, vr):
	return ['skip']

def s_roundedRect(rect, hr, vr):
	return ['skip']

def s(value):
	return ['s', value]

def øs(value):
	return ['skip']

def s_s(value):
	return ['skip']

def scale(scaleX, scaleY=None, center=None):
	return ['scale', scaleX, scaleY, center]

def øscale(scaleX, scaleY=None, center=None):
	return ['skip']

def s_scale(scaleX, scaleY=None, center=None):
	return ['skip']

def scaleToHeight(h):
	return ['scaleToHeight', h]

def øscaleToHeight(h):
	return ['skip']

def s_scaleToHeight(h):
	return ['skip']

def scaleToRect(rect, preserveAspect=True):
	return ['scaleToRect', rect, preserveAspect]

def øscaleToRect(rect, preserveAspect=True):
	return ['skip']

def s_scaleToRect(rect, preserveAspect=True):
	return ['skip']

def scaleToWidth(w):
	return ['scaleToWidth', w]

def øscaleToWidth(w):
	return ['skip']

def s_scaleToWidth(w):
	return ['skip']

def scanlines(rect, sample=40, width=20, threshold=10):
	return ['scanlines', rect, sample, width, threshold]

def øscanlines(rect, sample=40, width=20, threshold=10):
	return ['skip']

def s_scanlines(rect, sample=40, width=20, threshold=10):
	return ['skip']

def semicircle(r, center, fext=0.5, rext=0.5):
	return ['semicircle', r, center, fext, rext]

def øsemicircle(r, center, fext=0.5, rext=0.5):
	return ['skip']

def s_semicircle(r, center, fext=0.5, rext=0.5):
	return ['skip']

def simplify():
	return ['simplify', ]

def øsimplify():
	return ['skip']

def s_simplify():
	return ['skip']

def sine(r, periods):
	return ['sine', r, periods]

def øsine(r, periods):
	return ['skip']

def s_sine(r, periods):
	return ['skip']

def skeleton(scale=1, returnSet=False):
	return ['skeleton', scale, returnSet]

def øskeleton(scale=1, returnSet=False):
	return ['skip']

def s_skeleton(scale=1, returnSet=False):
	return ['skip']

def skeletonPoints():
	return ['skeletonPoints', ]

def øskeletonPoints():
	return ['skip']

def s_skeletonPoints():
	return ['skip']

def skew(x=0, y=0, point=None):
	return ['skew', x, y, point]

def øskew(x=0, y=0, point=None):
	return ['skip']

def s_skew(x=0, y=0, point=None):
	return ['skip']

def slicec(contour_slice):
	return ['slicec', contour_slice]

def øslicec(contour_slice):
	return ['skip']

def s_slicec(contour_slice):
	return ['skip']

def smooth():
	return ['smooth', ]

def øsmooth():
	return ['skip']

def s_smooth():
	return ['skip']

def standingwave(r, periods, direction=1):
	return ['standingwave', r, periods, direction]

def østandingwave(r, periods, direction=1):
	return ['skip']

def s_standingwave(r, periods, direction=1):
	return ['skip']

def stroke(value):
	return ['stroke', value]

def østroke(value):
	return ['skip']

def s_stroke(value):
	return ['skip']

def strokeWidth(value):
	return ['strokeWidth', value]

def østrokeWidth(value):
	return ['skip']

def s_strokeWidth(value):
	return ['skip']

def subsegment(start=0, end=1):
	return ['subsegment', start, end]

def øsubsegment(start=0, end=1):
	return ['skip']

def s_subsegment(start=0, end=1):
	return ['skip']

def svg(file, gid, rect=Rect([0, 0, 0, 100])):
	return ['svg', file, gid, rect]

def øsvg(file, gid, rect=Rect([0, 0, 0, 100])):
	return ['skip']

def s_svg(file, gid, rect=Rect([0, 0, 0, 100])):
	return ['skip']

def sw(value):
	return ['sw', value]

def øsw(value):
	return ['skip']

def s_sw(value):
	return ['skip']

def tag(tag):
	return ['tag', tag]

def øtag(tag):
	return ['skip']

def s_tag(tag):
	return ['skip']

def take(slice):
	return ['take', slice]

def øtake(slice):
	return ['skip']

def s_take(slice):
	return ['skip']

def to_glyph(name=None, width=None):
	return ['to_glyph', name, width]

def øto_glyph(name=None, width=None):
	return ['skip']

def s_to_glyph(name=None, width=None):
	return ['skip']

def to_pen():
	return ['to_pen', ]

def øto_pen():
	return ['skip']

def s_to_pen():
	return ['skip']

def trackToRect(rect, pullToEdges=False, r=0):
	return ['trackToRect', rect, pullToEdges, r]

def øtrackToRect(rect, pullToEdges=False, r=0):
	return ['skip']

def s_trackToRect(rect, pullToEdges=False, r=0):
	return ['skip']

def transform(transform, transformFrame=True):
	return ['transform', transform, transformFrame]

def øtransform(transform, transformFrame=True):
	return ['skip']

def s_transform(transform, transformFrame=True):
	return ['skip']

def translate(x, y=None, transformFrame=True):
	return ['translate', x, y, transformFrame]

def øtranslate(x, y=None, transformFrame=True):
	return ['skip']

def s_translate(x, y=None, transformFrame=True):
	return ['skip']

def union(otherPen):
	return ['union', otherPen]

def øunion(otherPen):
	return ['skip']

def s_union(otherPen):
	return ['skip']

def ups():
	return ['ups', ]

def øups():
	return ['skip']

def s_ups():
	return ['skip']

def vl(value):
	return ['vl', value]

def øvl(value):
	return ['skip']

def s_vl(value):
	return ['skip']

def walk(callback, depth=0):
	return ['walk', callback, depth]

def øwalk(callback, depth=0):
	return ['skip']

def s_walk(callback, depth=0):
	return ['skip']

def xAlignToFrame(x=Edge.CenterX, th=0):
	return ['xAlignToFrame', x, th]

def øxAlignToFrame(x=Edge.CenterX, th=0):
	return ['skip']

def s_xAlignToFrame(x=Edge.CenterX, th=0):
	return ['skip']

def xor(otherPen):
	return ['xor', otherPen]

def øxor(otherPen):
	return ['skip']

def s_xor(otherPen):
	return ['skip']

def å(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return ['å', rect, x, y, th, tv, transformFrame]

def øå(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return ['skip']

def s_å(rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
	return ['skip']

def Glyphs(ufo, glyphNames):
	return ['Glyphs', ufo, glyphNames]

def øGlyphs(ufo, glyphNames):
	return ['skip']

def s_Glyphs(ufo, glyphNames):
	return ['skip']

def addOverlaps(idx1, idx2, which, outline=3, scale=1, xray=0):
	return ['addOverlaps', idx1, idx2, which, outline, scale, xray]

def øaddOverlaps(idx1, idx2, which, outline=3, scale=1, xray=0):
	return ['skip']

def s_addOverlaps(idx1, idx2, which, outline=3, scale=1, xray=0):
	return ['skip']

def alignToRects(rects, x=Edge.CenterX, y=Edge.CenterY, th=1, tv=1):
	return ['alignToRects', rects, x, y, th, tv]

def øalignToRects(rects, x=Edge.CenterX, y=Edge.CenterY, th=1, tv=1):
	return ['skip']

def s_alignToRects(rects, x=Edge.CenterX, y=Edge.CenterY, th=1, tv=1):
	return ['skip']

def append(pen):
	return ['append', pen]

def øappend(pen):
	return ['skip']

def s_append(pen):
	return ['skip']

def clearFrames():
	return ['clearFrames', ]

def øclearFrames():
	return ['skip']

def s_clearFrames():
	return ['skip']

def collapse(levels=100, onself=False):
	return ['collapse', levels, onself]

def øcollapse(levels=100, onself=False):
	return ['skip']

def s_collapse(levels=100, onself=False):
	return ['skip']

def collapseonce():
	return ['collapseonce', ]

def øcollapseonce():
	return ['skip']

def s_collapseonce():
	return ['skip']

def distribute(v=False):
	return ['distribute', v]

def ødistribute(v=False):
	return ['skip']

def s_distribute(v=False):
	return ['skip']

def distributeOnPath(path, offset=0, cc=None, notfound=None):
	return ['distributeOnPath', path, offset, cc, notfound]

def ødistributeOnPath(path, offset=0, cc=None, notfound=None):
	return ['skip']

def s_distributeOnPath(path, offset=0, cc=None, notfound=None):
	return ['skip']

def extend(pens):
	return ['extend', pens]

def øextend(pens):
	return ['skip']

def s_extend(pens):
	return ['skip']

def ffg(glyph_name):
	return ['ffg', glyph_name]

def øffg(glyph_name):
	return ['skip']

def s_ffg(glyph_name):
	return ['skip']

def fft(tag):
	return ['fft', tag]

def øfft(tag):
	return ['skip']

def s_fft(tag):
	return ['skip']

def filter(fn):
	return ['filter', fn]

def øfilter(fn):
	return ['skip']

def s_filter(fn):
	return ['skip']

def glyphs_named(glyph_name):
	return ['glyphs_named', glyph_name]

def øglyphs_named(glyph_name):
	return ['skip']

def s_glyphs_named(glyph_name):
	return ['skip']

def implode():
	return ['implode', ]

def øimplode():
	return ['skip']

def s_implode():
	return ['skip']

def indexed_subset(indices):
	return ['indexed_subset', indices]

def øindexed_subset(indices):
	return ['skip']

def s_indexed_subset(indices):
	return ['skip']

def insert(index, pen):
	return ['insert', index, pen]

def øinsert(index, pen):
	return ['skip']

def s_insert(index, pen):
	return ['skip']

def interleave(style_fn, direction=-1, recursive=True):
	return ['interleave', style_fn, direction, recursive]

def øinterleave(style_fn, direction=-1, recursive=True):
	return ['skip']

def s_interleave(style_fn, direction=-1, recursive=True):
	return ['skip']

def mfilter(fn):
	return ['mfilter', fn]

def ømfilter(fn):
	return ['skip']

def s_mfilter(fn):
	return ['skip']

def mmap(fn):
	return ['mmap', fn]

def ømmap(fn):
	return ['skip']

def s_mmap(fn):
	return ['skip']

def overlapPair(gn1, gn2, which, outline=3):
	return ['overlapPair', gn1, gn2, which, outline]

def øoverlapPair(gn1, gn2, which, outline=3):
	return ['skip']

def s_overlapPair(gn1, gn2, which, outline=3):
	return ['skip']

def overlapPairs(pairs, outline=3):
	return ['overlapPairs', pairs, outline]

def øoverlapPairs(pairs, outline=3):
	return ['skip']

def s_overlapPairs(pairs, outline=3):
	return ['skip']

def pfilter(fn):
	return ['pfilter', fn]

def øpfilter(fn):
	return ['skip']

def s_pfilter(fn):
	return ['skip']

def pmap(fn):
	return ['pmap', fn]

def øpmap(fn):
	return ['skip']

def s_pmap(fn):
	return ['skip']

def print_tree(depth=0):
	return ['print_tree', depth]

def øprint_tree(depth=0):
	return ['skip']

def s_print_tree(depth=0):
	return ['skip']

def reversePens():
	return ['reversePens', ]

def øreversePens():
	return ['skip']

def s_reversePens():
	return ['skip']

def rp():
	return ['rp', ]

def ørp():
	return ['skip']

def s_rp():
	return ['skip']

def tagged(tag):
	return ['tagged', tag]

def øtagged(tag):
	return ['skip']

def s_tagged(tag):
	return ['skip']

def track(t, v=False):
	return ['track', t, v]

def øtrack(t, v=False):
	return ['skip']

def s_track(t, v=False):
	return ['skip']

def understroke(s=0, sw=5, outline=False, dofill=0):
	return ['understroke', s, sw, outline, dofill]

def øunderstroke(s=0, sw=5, outline=False, dofill=0):
	return ['skip']

def s_understroke(s=0, sw=5, outline=False, dofill=0):
	return ['skip']

