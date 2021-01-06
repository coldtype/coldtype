import math, tempfile, pickle, inspect
from enum import Enum
from copy import deepcopy
from pathlib import Path
from time import sleep
from pathlib import Path

from typing import Optional
from typing import Callable
#from collections.abc import Callable

from fontTools.misc.transform import Transform

from coldtype.geometry import Rect, Edge, Point, txt_to_edge
from coldtype.color import normalize_color
import coldtype.pens.drawbot_utils as dbu


from noise import pnoise1


class DATPenLikeObject():
    _context = None
    _pen_class = None
    _precompose_save = None

    def align(self, rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
        x = txt_to_edge(x)
        y = txt_to_edge(y)
        b = self.getFrame(th=th, tv=tv)
        
        xoff = 0
        if x != None:
            if x == Edge.CenterX:
                xoff = -b.x + rect.x + rect.w/2 - b.w/2
            elif x == Edge.MinX:
                xoff = -(b.x-rect.x)
            elif x == Edge.MaxX:
                xoff = -b.x + rect.x + rect.w - b.w
        
        yoff = 0
        if y != None:
            if y == Edge.CenterY:
                yoff = -b.y + rect.y + rect.h/2 - b.h/2
            elif y == Edge.MaxY:
                yoff = (rect.y + rect.h) - (b.h + b.y)
            elif y == Edge.MinY:
                yoff = -(b.y-rect.y)
        
        diff = rect.w - b.w
        return self.translate(xoff, yoff, transformFrame=transformFrame)
    
    å = align

    def xAlignToFrame(self, x=Edge.CenterX, th=0):
        if self.frame:
            return self.align(self.getFrame(th=th, tv=0), x=x, transformFrame=0, th=1)
        else:
            raise Exception("No Frame")
    
    def center_on_point(self, rect, pt):
        return self.translate(rect.w/2-pt[0], rect.h/2-pt[1])
    
    def pen(self):
        """Return a single-pen representation of this pen(set)."""
        return self
    
    def to_pen(self):
        return self.pen()

    def cast(self, _class, *args):
        """Quickly cast to a (different) subclass."""
        return _class(self, *args)

    def copy(self, with_data=False):
        """Make a totally fresh copy; useful given the DATPen’s general reliance on mutable state."""
        dp = self.single_pen_class()
        self.replay(dp)
        for tag, attrs in self.attrs.items():
            dp.attr(tag, **attrs)
        dp.glyphName = self.glyphName
        if with_data:
            dp.data = self.data
            if self.typographic:
                dp.frame = self.frame
                dp.typographic = True
        return dp

    def tag(self, tag):
        """For conveniently marking a DATPen(Set) w/o having to put it into some other data structure."""
        self._tag = tag
        return self

    def add_data(self, key, value=None):
        if value is None:
            self.data = key
        else:
            self.data[key] = value
        return self
    
    def editable(self, tag):
        self.tag(tag)
        self.editable = True
        return self
    
    def getTag(self):
        """Retrieve the tag (could probably be a real property)"""
        return self._tag
    
    def contain(self, rect):
        """For conveniently marking an arbitrary `Rect` container."""
        self.container = rect
        return self
    
    def v(self, v):
        self.visible = bool(v)
        return self
    
    def a(self, v):
        self._alpha = v
        return self

    def f(self, *value):
        """Get/set a (f)ill"""
        if value:
            return self.attr(fill=value)
        else:
            return self.attr(field="fill")
    
    fill = f
    
    def s(self, *value):
        """Get/set a (s)troke"""
        if value:
            return self.attr(stroke=value)
        else:
            return self.attr(field="stroke")
    
    stroke = s
    
    def sw(self, value):
        """Get/set a (s)troke (w)idth"""
        if value:
            return self.attr(strokeWidth=value)
        else:
            return self.attr(field="strokeWidth")
    
    strokeWidth = sw

    def img(self, src=None, rect=Rect(0, 0, 500, 500), pattern=True, opacity=1.0):
        """Get/set an image fill"""
        if src:
            return self.attr(image=dict(src=src, rect=rect, pattern=pattern, opacity=opacity))
        else:
            return self.attr(field="image")
    
    def img_opacity(self, opacity, key="default"):
        img = self.attr(key, "image")
        if not img:
            raise Exception("No image found")
        self.attrs[key]["image"]["opacity"] = opacity
        return self
    
    image = img

    def shadow(self, radius=10, color=(0, 0.3), clip=None):
        return self.attr(shadow=dict(color=normalize_color(color), radius=radius, clip=clip))
    
    def blendmode(self, blendmode=None):
        if blendmode:
            return self.attr(blendmode=blendmode)
        else:
            return self.attr(field="blendmode")
        return self
    
    def removeBlanks(self):
        """If this is blank, `return True` (for recursive calls from DATPens)."""
        return len(self.value) == 0
    
    def clearFrame(self):
        """Remove the DATPen frame."""
        self.frame = None
        return self
    
    def addFrame(self, frame, typographic=False, passthru=False):
        """Add a new frame to the DATPen, replacing any old frame. Passthru ignored, there for compatibility"""
        self.frame = frame
        if typographic:
            self.typographic = True
        return self
    
    def frameSet(self, th=False, tv=False):
        """Return a new DATPen representation of the frame of this DATPen."""
        return self.single_pen_class(fill=("random", 0.25)).rect(self.getFrame(th=th, tv=tv))
    
    def translate(self, x, y=None, transformFrame=True):
        """Translate this shape by `x` and `y` (pixel values)."""
        if y is None:
            y = x
        img = self.img()
        if img:
            img["rect"] = img["rect"].offset(x, y)
        return self.transform(Transform(1, 0, 0, 1, x, y), transformFrame=transformFrame)
    
    def scale(self, scaleX, scaleY=None, center=None):
        """Scale this shape by a percentage amount (1-scale)."""
        t = Transform()
        if center != False:
            point = self.bounds().point("C") if center == None else center # maybe should be getFrame()?
            t = t.translate(point.x, point.y)
        t = t.scale(scaleX, scaleY or scaleX)
        if center != False:
            t = t.translate(-point.x, -point.y)
        return self.transform(t)
    
    def scaleToRect(self, rect, preserveAspect=True, shrink_only=False):
        """Scale this shape into a `Rect`."""
        bounds = self.bounds()
        h = rect.w / bounds.w
        v = rect.h / bounds.h
        if preserveAspect:
            scale = h if h < v else v
            if shrink_only and scale >= 1:
                return self
            return self.scale(scale)
        else:
            if shrink_only and (h >= 1 or v >= 1):
                return self
            return self.scale(h, v)
    
    def scaleToWidth(self, w, shrink_only=False):
        """Scale this shape horizontally"""
        b = self.bounds()
        if shrink_only and b.w < w:
            return self
        else:
            return self.scale(w / self.bounds().w, 1)
    
    def scaleToHeight(self, h, shrink_only=False):
        """Scale this shape horizontally"""
        b = self.bounds()
        if shrink_only and b.h < h:
            return self
        return self.scale(1, h / self.bounds().h)
    
    def trackToRect(self, rect, pullToEdges=False, r=0):
        """Distribute pens evenly within a frame"""
        if len(self) == 1:
            return self.align(rect)
        total_width = 0
        pens = self.pens
        if r:
            pens = list(reversed(pens))
        start_x = pens[0].getFrame(th=pullToEdges).x
        end_x = pens[-1].getFrame(th=pullToEdges).point("SE").x
        # TODO easy to knock out apostrophes here based on a callback, last "actual" frame
        total_width = end_x - start_x
        leftover_w = rect.w - total_width
        tracking_value = leftover_w / (len(self)-1)
        if pullToEdges:
            xoffset = rect.x - pens[0].bounds().x
        else:
            xoffset = rect.x - pens[0].getFrame().x
        for idx, p in enumerate(pens):
            if idx == 0:
                p.translate(xoffset, 0)
            else:
                p.translate(xoffset+tracking_value*idx, 0)
        return self
    
    def skew(self, x=0, y=0, point=None):
        t = Transform()
        if not point:
            point = self.bounds().point("C") # maybe should be getFrame()?
        t = t.translate(point.x, point.y)
        t = t.skew(x, y)
        t = t.translate(-point.x, -point.y)
        return self.transform(t)
    
    def rotate(self, degrees, point=None):
        """Rotate this shape by a degree (in 360-scale, counterclockwise)."""
        t = Transform()
        if not point:
            point = self.bounds().point("C") # maybe should be getFrame()?
        t = t.translate(point.x, point.y)
        t = t.rotate(math.radians(degrees))
        t = t.translate(-point.x, -point.y)
        return self.transform(t, transformFrame=False)
    
    def filmjitter(self, doneness, base=0, speed=(10, 20), scale=(2, 3), octaves=16):
        """
        An easy way to make something move in a way reminiscent of misregistered film
        """
        nx = pnoise1(doneness*speed[0], base=base, octaves=octaves)
        ny = pnoise1(doneness*speed[1], base=base+10, octaves=octaves)
        return self.translate(nx * scale[0], ny * scale[1])
    
    def walk(self, callback:Callable[["DATPenLikeObject", int, dict], None], depth=0, visible_only=False, parent=None):
        if visible_only and not self.visible:
            return
        
        if parent:
            self._parent = parent
        
        is_dps = hasattr(self, "pens")
        if is_dps:
            callback(self, -1, dict(depth=depth))
            for pen in self.pens:
                pen.walk(callback, depth=depth+1, visible_only=visible_only, parent=self)
            callback(self, 1, dict(depth=depth))
        else:
            callback(self, 0, dict(depth=depth))
    
    def all_pens(self):
        pens = []
        if hasattr(self, "pens"):
            pens = self.collapse().pens
        if isinstance(self, self.single_pen_class):
            pens = [self]
        
        for pen in pens:
            if pen:
                if hasattr(pen, "pens"):
                    for _p in pen.collapse().pens:
                        if _p:
                            yield _p
                else:
                    yield pen
    
    def _db_drawPath(self):
        for dp in list(self.all_pens()):
            with dbu.db.savedState():
                dbu.db.fill(None)
                dbu.db.stroke(None)
                dbu.db.strokeWidth(0)
                for attr, value in dp.allStyledAttrs().items():
                    if attr == "fill":
                        dbu.db_fill(value)
                    elif attr == "stroke":
                        dbu.db_stroke(value.get("weight", 1), value.get("color"), None)
                    dbu.db.drawPath(dp.bp())
    
    def db_drawPath(self, rect=None, filters=[]):
        try:
            if rect and len(filters) > 0:
                im = dbu.db.ImageObject()
                with im:
                    dbu.db.size(*rect.wh())
                    self._db_drawPath()
                for filter_name, filter_kwargs in filters:
                    getattr(im, filter_name)(**filter_kwargs)
                x, y = im.offset()
                dbu.db.image(im, (x, y))
            else:
                self._db_drawPath()
            return self
        except ImportError:
            print("DrawBot not installed!")
            return self
    
    def noop(self, *args, **kwargs):
        """Does nothing"""
        return self
    
    def sleep(self, time):
        """Sleep call within the chain (if you want to measure something)"""
        sleep(time)
        return self

    def chain(self, fn:[["DATPenLikeObject"], None]):
        """
        For simple take-one callback functions in a chain
        """
        fn(self)
        return self
    
    def cond(self, condition, if_true: Callable[["DATPenLikeObject"], None], if_false=Callable[["DATPenLikeObject"], None]):
        if condition:
            if_true(self)
        else:
            if_false(self)
        return self
    
    def _get_renderer_state(self, pen_class, context):
        if not pen_class:
            pen_class = DATPenLikeObject._pen_class
        if not pen_class:
            raise Exception("No _pen_class")

        if not context:
            context = DATPenLikeObject._context
        elif context == -1:
            context = None
        
        return pen_class, context
    
    def precompose(self, rect, placement=None, opacity=1, scale=1, pen_class=None, context=None):
        pc, ctx = self._get_renderer_state(pen_class, context)
        img = pc.Precompose(self, rect, context=ctx, scale=scale, disk=DATPenLikeObject._precompose_save)
        return self.single_pen_class().rect(placement or rect).img(img, (placement or rect), False, opacity).f(None)
    
    def rasterized(self, rect, scale=1, pen_class=None, context=None):
        """
        Same as precompose but returns the Image created rather
        than setting that image as the attr-image of this pen
        """
        pc, ctx = self._get_renderer_state(pen_class, context)
        return pc.Precompose(self, rect, scale=scale, context=ctx, disk=DATPenLikeObject._precompose_save)
    
    def mod_pixels(self, rect, scale=0.1, mod=lambda rgba: None, pen_class=None, context=None):
        import skia
        import PIL.Image
        rasterized = self.rasterized(rect, scale=scale, pen_class=pen_class, context=context)
        pi = PIL.Image.fromarray(rasterized, "RGBa")
        for x in range(pi.width):
            for y in range(pi.height):
                r, g, b, a = pi.getpixel((x, y))
                res = mod((r, g, b, a))
                if res:
                    pi.putpixel((x, y), tuple(res))
        out = skia.Image.frombytes(pi.convert('RGBA').tobytes(), pi.size, skia.kRGBA_8888_ColorType)
        return self.single_pen_class().rect(rect).img(out, rect, False).f(None)

    def potrace(self, rect, poargs=[], invert=True, pen_class=None, context=None):
        import skia
        from PIL import Image
        from pathlib import Path
        from subprocess import run
        from fontTools.svgLib import SVGPath

        pc, ctx = self._get_renderer_state(pen_class, context)

        img = pc.Precompose(self, rect, context=ctx)
        pilimg = Image.fromarray(img.convert(alphaType=skia.kUnpremul_AlphaType))
        binpo = Path("bin/potrace")
        if not binpo.exists():
            binpo = Path(__file__).parent.parent.parent / "bin/potrace"

        with tempfile.NamedTemporaryFile(prefix="coldtype_tmp", suffix=".bmp") as tmp_bmp:
            pilimg.save(tmp_bmp.name)
            rargs = [str(binpo), "-s"]
            if invert:
                rargs.append("--invert")
            rargs.extend([str(x) for x in poargs])
            rargs.extend(["-o", "-", "--", tmp_bmp.name])
            if False:
                print(">>>", " ".join(rargs))
            result = run(rargs, capture_output=True)
            t = Transform()
            t = t.scale(0.1, 0.1)
            svgp = SVGPath.fromstring(result.stdout, transform=t)
            dp = self.single_pen_class()
            svgp.draw(dp)
            return dp.f(0)
    
    def phototype(self, rect, blur=5, cut=127, cutw=3, fill=1, pen_class=None, context=None, rgba=[0, 0, 0, 1], luma=True):
        r, g, b, a = rgba
        pc, ctx = self._get_renderer_state(pen_class, context)

        import skia
        import coldtype.filtering as fl

        first_pass = dict(ImageFilter=fl.blur(blur))
        
        if luma:
            first_pass["ColorFilter"] = skia.LumaColorFilter.Make()

        cut_filters = [
            fl.as_filter(
                fl.contrast_cut(cut, cutw),
                a=a, r=r, g=g, b=b)]
            
        if fill is not None:
            cut_filters.append(fl.fill(normalize_color(fill)))

        return (self
            .precompose(rect, pen_class=pc, context=ctx)
            .attr(skp=first_pass)
            .precompose(rect, pen_class=pc, context=ctx)
            .attr(skp=dict(
                ColorFilter=fl.compose(*cut_filters))))
    
    def color_phototype(self, rect, blur=5, cut=127, cutw=15, pen_class=None, context=None, rgba=[1, 1, 1, 1]):
        return self.phototype(rect, blur, 255-cut, cutw, fill=None, pen_class=pen_class, context=context, rgba=rgba, luma=False)
    
    def DiskCached(path:Path, build_fn: Callable[[], "DATPenLikeObject"]):
        dpio = None
        fn_src = inspect.getsource(build_fn)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            dpio = build_fn()
        else:
            try:
                dpio = pickle.load(open(path, "rb"))
                old_fn_src = dpio.data.get("fn_src", "")
                if fn_src != old_fn_src:
                    dpio = build_fn()
            except pickle.PickleError:
                dpio = build_fn()
        
        dpio.data["fn_src"] = fn_src
        pickle.dump(dpio, open(path, "wb"))
        return dpio
    
    def pickle(self, dst):
        dst.parent.mkdir(parents=True, exist_ok=True)
        pickle.dump(self, open(str(dst), "wb"))
        return self
    
    def Unpickle(self, src):
        return pickle.load(open(str(src), "rb"))