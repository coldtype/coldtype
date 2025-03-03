from fontTools.pens.recordingPen import RecordingPen
import skia, tempfile, math
from subprocess import run
from functools import reduce
from random import Random, randint
from pathlib import Path

from fontTools.svgLib import SVGPath
from fontTools.misc.transform import Transform

from coldtype.fx.chainable import Chainable
from coldtype.color import normalize_color, bw
from coldtype.img.blendmode import BlendMode
from coldtype.runon.path import P
from coldtype.pens.skiapen import SkiaPen
from coldtype.geometry import Rect

import coldtype.skiashim as skiashim

SKIA_CONTEXT = None

class Skfi():
    @staticmethod
    def contrast_cut(mp=127, w=5):
        ct = bytearray(256)
        for i in range(256):
            if i < mp - w:
                ct[i] = 0
            elif i < mp:
                ct[i] = int((255.0/2)*(1-(mp-i)/w))
            elif i == mp:
                ct[i] = 127
            elif i < mp + w:
                ct[i] = int(127+(255.0/2)*((i-mp)/w))
            else:
                ct[i] = 255
        return ct

    @staticmethod
    def as_filter(lut, a=1, r=0, g=0, b=0):
        args = [lut if x else None for x in [a, r, g, b]]
        return skia.TableColorFilter.MakeARGB(*args)

    @staticmethod
    def compose(*filters):
        # TODO check if ColorFilter or something else?
        return reduce(lambda acc, el: skia.ColorFilters.Compose(el, acc) if acc else el, reversed(filters), None)

    @staticmethod
    def fill(color):
        r, g, b, a = color
        return skia.ColorFilters.Matrix([
            0, 0, 0, 0, r,
            0, 0, 0, 0, g,
            0, 0, 0, 0, b,
            0, 0, 0, a, 0,
        ])

    @staticmethod
    def blur(blur):
        try:
            xblur, yblur = blur
        except:
            xblur, yblur = blur, blur

        return skiashim.imageFilters_Blur(xblur, yblur)

    @staticmethod
    def improved_noise(e, xo=0, yo=0, xs=1, ys=1, base=1):
        return skiashim.make_improved_noise(e, xo, yo, xs, ys, 0.015, 0.015, 3, base)
    
    # straight from the chromium source https://chromium.googlesource.com/chromium/blink/+/refs/heads/main/Source/platform/graphics/filters/FEColorMatrix.cpp

    @staticmethod
    def huerotate(hue):
        cosHue = math.cos(hue * math.pi / 180);
        sinHue = math.sin(hue * math.pi / 180);
        matrix = [0 for _ in range(0, 20)]
        matrix[0] = 0.213 + cosHue * 0.787 - sinHue * 0.213;
        matrix[1] = 0.715 - cosHue * 0.715 - sinHue * 0.715;
        matrix[2] = 0.072 - cosHue * 0.072 + sinHue * 0.928;
        matrix[3] = matrix[4] = 0;
        matrix[5] = 0.213 - cosHue * 0.213 + sinHue * 0.143;
        matrix[6] = 0.715 + cosHue * 0.285 + sinHue * 0.140;
        matrix[7] = 0.072 - cosHue * 0.072 - sinHue * 0.283;
        matrix[8] = matrix[9] = 0;
        matrix[10] = 0.213 - cosHue * 0.213 - sinHue * 0.787;
        matrix[11] = 0.715 - cosHue * 0.715 + sinHue * 0.715;
        matrix[12] = 0.072 + cosHue * 0.928 + sinHue * 0.072;
        matrix[13] = matrix[14] = 0;
        matrix[15] = matrix[16] = matrix[17] = 0;
        matrix[18] = 1;
        matrix[19] = 0;
        return skia.ColorFilters.Matrix(matrix)
    
    @staticmethod
    def saturate(s):
        matrix = [0 for _ in range(0, 20)]
        matrix[0] = 0.213 + 0.787 * s
        matrix[1] = 0.715 - 0.715 * s
        matrix[2] = 0.072 - 0.072 * s
        matrix[3] = matrix[4] = 0
        matrix[5] = 0.213 - 0.213 * s
        matrix[6] = 0.715 + 0.285 * s
        matrix[7] = 0.072 - 0.072 * s
        matrix[8] = matrix[9] = 0
        matrix[10] = 0.213 - 0.213 * s
        matrix[11] = 0.715 - 0.715 * s
        matrix[12] = 0.072 + 0.928 * s
        matrix[13] = matrix[14] = 0
        matrix[15] = matrix[16] = matrix[17] = 0
        matrix[18] = 1
        matrix[19] = 0
        return skia.ColorFilters.Matrix(matrix)
    
    @staticmethod
    def temp(t):
        return skia.ColorFilters.Matrix([
            1+t, 0, 0, 0, 0,
            0, 1, 0, 0, 0,
            0, 0, 1-t, 0, 0,
            0, 0, 0, 1, 0,
        ])
    
    @staticmethod
    def tone(t):
        return skia.ColorFilters.Matrix([
            1+t, 0, 0, 0, 0,
            0, 1-t, 0, 0, 0,
            0, 0, 1+t, 0, 0,
            0, 0, 0, 1, 0,
        ])
    
    @staticmethod
    def expose(t):
        return skia.ColorFilters.Matrix([
            t, 0, 0, 0, 0,
            0, t, 0, 0, 0,
            0, 0, t, 0, 0,
            0, 0, 0, 1, 0,
        ])
    
    @staticmethod
    def red():
        return skia.ColorFilters.Matrix([
            1, 0, 0, 0, 0,
            1, 0, 0, 0, 0,
            1, 0, 0, 0, 0,
            0, 0, 0, 1, 0,
        ])
    
    @staticmethod
    def green():
        return skia.ColorFilters.Matrix([
            0, 1, 0, 0, 0,
            0, 1, 0, 0, 0,
            0, 1, 0, 0, 0,
            0, 0, 0, 1, 0,
        ])
    
    @staticmethod
    def blue():
        return skia.ColorFilters.Matrix([
            0, 0, 1, 0, 0,
            0, 0, 1, 0, 0,
            0, 0, 1, 0, 0,
            0, 0, 0, 1, 0,
        ])
    
    @staticmethod
    def invert():
        return skia.ColorFilters.Matrix([
            -1,  0,  0,  0,  1,  # Red
            0, -1,  0,  0,  1,  # Green
            0,  0, -1,  0,  1,  # Blue
            0,  0,  0,  1,  0   # Alpha (unchanged)
        ])

# CHAINABLES

def spackle(xo=None, yo=None,
    xs=0.85, ys=0.85, base=None,
    cut=240, cutw=5, fill=bw(1)
    ):
    r1 = Random()
    r1.seed(0)

    if not xo:
        xo = r1.randint(-500, 500)
    if not yo:
        yo = r1.randint(-500, 500)
    if base is None:
        base = randint(0, 5000)
    
    def _spackle(pen):
        return (pen.f(1)
            .attr(skp=dict(
                Shader=(Skfi.improved_noise(1,
                    xo=xo, yo=yo, xs=xs, ys=ys, base=base)
                    .makeWithColorFilter(Skfi.compose(
                        Skfi.fill(fill),
                        Skfi.as_filter(Skfi.contrast_cut(cut, cutw)),
                        skia.LumaColorFilter.Make()))))))
    return _spackle


def fill(c):
    """Chainable function for filling everything in pen/image-on-pen with a single color"""
    c = normalize_color(c)
    def _fill(pen):
        return pen.attr(skp=dict(
            ColorFilter=Skfi.fill(c)))
    return _fill


try:
    import potrace as potracer
    turn_policy = potracer.POTRACE_TURNPOLICY_MINORITY
except ImportError:
    turn_policy = None
    pass


def potrace(rect, invert=True,
    turdsize=2, # 0-infinity
    turnpolicy=turn_policy,
    alphamax=1.0, #  0.0 (polygon) to 1.3333 (no corners)
    opticurve=1,
    opttolerance=0.2, # 0 -1
    ):
    """Chainable function for tracing a pen/image-on-pen ; can be combined with a previous call to phototype for better control of blurring/edges"""
    from PIL import Image

    def _potrace(pen):
        if invert:
            pen = pen.copy().layer(1, lambda _: P(rect).f(1).blendmode(BlendMode.Difference))

        res = SkiaPen.Precompose(pen, rect, SKIA_CONTEXT)
        pilimg = Image.fromarray(res.convert(alphaType=skia.kUnpremul_AlphaType))
        bmp = potracer.Bitmap(pilimg)
        path = bmp.trace(turdsize, turnpolicy, alphamax, opticurve, opttolerance)

        op = P()
        for curve in path:
            op.moveTo(curve.start_point.x, curve.start_point.y)
            for segment in curve:
                if segment.is_corner:
                    op.lineTo(segment.c.x, segment.c.y)
                else:
                    op.curveTo(
                        (segment.c1.x, segment.c1.y),
                        (segment.c2.x, segment.c2.y),
                        (segment.end_point.x, segment.end_point.y))
            op.closePath()

        op.scale(1, -1, point=rect.pc)
        return op
    return _potrace

def precompose(rect,
    placement=None,
    opacity=1,
    scale=1,
    disk=False,
    style=None,
    ):
    def _precompose(pen):
        img = SkiaPen.Precompose(pen, rect,             
            context=SKIA_CONTEXT,
            scale=scale,
            disk=disk,
            style=style)
        
        return (P()
            .rect(placement or rect)
            .img(img, (placement or rect), False, opacity)
            .f(None))
    
    return Chainable(_precompose)


def rasterized(rect, scale=1, wrapped=False):
    """
    Same as precompose but returns the Image created rather
    than setting that image as the attr-image of this pen
    """
    from coldtype.img.skiaimage import SkiaImage
    def _rasterized(pen):
        precomposed = SkiaPen.Precompose(pen, rect, scale=scale, context=SKIA_CONTEXT, disk=False)
        if wrapped:
            return SkiaImage(precomposed)
        else:
            return precomposed
    return _rasterized, dict(returns=SkiaImage if wrapped else skia.Image)


def rasterize(rect, path):
    def _rasterize(pen):
        pen.ch(precompose(rect)).img().get("src").save(str(Path(path).expanduser()), skia.kPNG)
        return None
    return _rasterize


def mod_pixels(rect, scale=0.1, mod=lambda rgba: None):
    import PIL.Image
    
    def _mod_pixels(pen):
        raster = pen.ch(rasterized(rect, scale=scale))
        pi = PIL.Image.fromarray(raster, "RGBa")
        for x in range(pi.width):
            for y in range(pi.height):
                r, g, b, a = pi.getpixel((x, y))
                res = mod((r, g, b, a))
                if res:
                    pi.putpixel((x, y), tuple(res))
        out = skia.Image.frombytes(pi.convert('RGBA').tobytes(), pi.size, skia.kRGBA_8888_ColorType)
        return (P()
            .rect(rect)
            .img(out, rect, False)
            .f(None))
    
    return _mod_pixels


def warp_image(image, rect, mod):
    from skimage import img_as_ubyte
    from skimage.transform import warp
    import numpy as np

    image_data = image.toarray()
    image_data = image_data.reshape(rect.h, rect.w, 4)
    image_rgb = image_data[..., :3]
    image_rgb_uint8 = img_as_ubyte(image_rgb)
    
    swirled = warp(image_rgb_uint8,
        mod,
        output_shape=image_rgb_uint8.shape)

    swirled_uint8 = (swirled * 255).astype(np.uint8)
    image_rgb_uint8 = swirled_uint8

    height, width, channels = image_rgb_uint8.shape
    if channels == 3:
        image_rgba = np.dstack((image_rgb_uint8, np.full((height, width), 255, dtype=np.uint8)))
    else:
        image_rgba = image_rgb_uint8
    
    return skia.Image.fromarray(image_rgba)


def warp(rect, mod):
    from skimage import img_as_ubyte
    from skimage.transform import warp
    import numpy as np

    def _warp(pen):
        raster = pen.ch(rasterized(rect))
        image_data = raster.toarray()
        image_data = image_data.reshape(rect.w, rect.h, 4)
        image_rgb = image_data[..., :3]
        image_rgb_uint8 = img_as_ubyte(image_rgb)
        
        swirled = warp(image_rgb_uint8,
            mod,
            output_shape=image_rgb_uint8.shape)
    
        swirled_uint8 = (swirled * 255).astype(np.uint8)
        image_rgb_uint8 = swirled_uint8

        height, width, channels = image_rgb_uint8.shape
        if channels == 3:
            image_rgba = np.dstack((image_rgb_uint8, np.full((height, width), 255, dtype=np.uint8)))
        else:
            image_rgba = image_rgb_uint8
        
        out = skia.Image.fromarray(image_rgba)
        return (P()
            .rect(rect)
            .img(out, rect, False)
            .f(None))
    
    return _warp


def luma(rect, fill=None):
    """Chainable function for converting light part of pen/image-on-pen into an alpha channel; see `LumaColorFilter <https://kyamagu.github.io/skia-python/reference/skia.LumaColorFilter.html>`_"""
    def _luma(pen):
        pen = pen.ch(precompose(rect))
        pen.attr(skp=dict(ColorFilter=skia.LumaColorFilter.Make()))
        if fill is not None:
            pen = (pen
                .ch(precompose(rect))
                .attr(skp=dict(ColorFilter=Skfi.fill(normalize_color(fill)))))
        return pen
    return _luma

def phototype(rect=None,
    blur=5,
    cut=127,
    cutw=3,
    fill=1,
    rgba=[0, 0, 0, 1],
    luma=True
    ):
    """Chainable function for “exposing” a pen/image-on-pen in the manner of lithofilm, i.e. light-parts are kept, dark parts are thrown away (turned into alpha)"""
    def _phototype(pen):
        nonlocal rect
        if rect is None:
            rect = pen.ambit().inset(-50)

        r, g, b, a = rgba

        first_pass = dict(ImageFilter=Skfi.blur(blur))
        
        if luma:
            first_pass["ColorFilter"] = skia.LumaColorFilter.Make()

        cut_filters = [
            Skfi.as_filter(
                Skfi.contrast_cut(cut, cutw),
                a=a, r=r, g=g, b=b)]
            
        if fill is not None:
            cut_filters.append(Skfi.fill(normalize_color(fill)))

        return (pen
            .ch(precompose(rect))
            .attr(skp=first_pass)
            .ch(precompose(rect))
            .attr(skp=dict(
                ColorFilter=Skfi.compose(*cut_filters))))
    
    return Chainable(_phototype)


def color_phototype(rect,
    blur=5,
    cut=127,
    cutw=15,
    rgba=[1, 1, 1, 1]
    ):
    return phototype(rect, blur, 255-cut, cutw, fill=None, rgba=rgba, luma=False)

def huerotate(c):
    c = c*360%360
    def _fill(pen):
        return pen.attr(skp=dict(ColorFilter=Skfi.huerotate(c)))
    return _fill

def saturate(c):
    #c = c*360%360
    def _fill(pen):
        return pen.attr(skp=dict(ColorFilter=Skfi.saturate(c)))
    return _fill

def expose(t):
    def _fill(pen):
        return pen.attr(skp=dict(ColorFilter=Skfi.expose(t)))
    return _fill

def invert():
    def _fill(pen):
        return pen.attr(skp=dict(ColorFilter=Skfi.invert()))
    return _fill

def temp(t):
    def _fill(pen):
        return pen.attr(skp=dict(ColorFilter=Skfi.temp(t)))
    return _fill

def tone(t):
    def _fill(pen):
        return pen.attr(skp=dict(ColorFilter=Skfi.tone(t)))
    return _fill

def temptone(temp, tone):
    def _fill(pen):
        pen.attr(skp=dict(ColorFilter=Skfi.compose(Skfi.temp(temp), Skfi.tone(tone))))
    return _fill

def channel(c):
    filters = dict(red=Skfi.red, green=Skfi.green, blue=Skfi.blue)
    
    if isinstance(c, str):
        filter = filters[c]
    else:
        filter = list(filters.values())[c]
    
    def _fill(pen):
        pen.attr(skp=dict(ColorFilter=filter()))
    return _fill

def rgbmod(rect, r=None, g=None, b=None):
    def _rgbmod(p):
        raster = p.ch(rasterized(rect, wrapped=True))
        return (P(
            raster.copy()
                .in_pen()
                .f(-1)
                .ch(channel(0))
                .ch(luma(rect, fill=1))
                .ch(r)
                if r else None,
            raster.copy()
                .in_pen()
                .f(-1)
                .ch(channel(1))
                .ch(luma(rect, fill=1))
                .ch(g)
                if g else None,
            raster.copy()
                .in_pen()
                .f(-1)
                .ch(channel(2))
                .ch(luma(rect, fill=1))
                .ch(b)
                if b else None,
            ))
    return _rgbmod

def shake(seg_length=2, deviation=2, seed=0):
    """shake up the path"""
    def _shake(p):
        effect = skia.DiscretePathEffect.Make(
            seg_length, deviation, seed)
        return p.attr(skp=dict(PathEffect=effect))
    return _shake

def round_corners(roundedness=20):
    def _round(p):
        effect = skia.CornerPathEffect.Make(roundedness)
        return p.attr(skp=dict(PathEffect=effect))
    return _round

def draw_canvas(r:Rect, draw_function:callable, in_pen=False):
    from coldtype.img.skiaimage import SkiaImage
    from coldtype.fx.skia import SKIA_CONTEXT
    from coldtype.pens.skiapen import SkiaPen

    def draw(canvas):
        return draw_function(r, canvas)

    img = SkiaImage(SkiaPen.Precompose(draw, r, context=SKIA_CONTEXT))
    
    if in_pen:
        return img.in_pen().f(-1)
    else:
        return img


def text_image(r:Rect, in_pen=True):
    """
    Requires that annotate=1 is passed to original StSt or Style
    """
    from coldtype.img.skiaimage import SkiaImage

    def _text_image(p:P):
        try:
            stst = p._stst
            text = stst.text
        except AttributeError:
            try:
                stst = p.parent()._stst
                text = p.data("glyphName") # TODO this isn't a good assumption
            except AttributeError:
                stst = None
                text = None
        
        if not stst:
            print("! please pass annotate=1 to original `StSt` !")
            return p
        
        style = stst.style

        skia_font = skia.Font(skia.Typeface.MakeFromFile(str(style.font.path)), style.fontSize)

        builder = skia.TextBlobBuilder()
        builder.allocRun(text, skia_font, 0, 0)
        blob = builder.make()

        x, y = p.ambit(tx=0, ty=0).xy()

        def draw(r, canvas):
            canvas.drawTextBlob(blob, x, r.h-y, skia.Paint(AntiAlias=True))
        
        return draw_canvas(r, draw, in_pen=in_pen)
    
    return _text_image, dict(returns=P if in_pen else SkiaImage)

def image_shader(r:Rect, image, sksl, in_pen=True):
    """
    Requires that annotate=1 is passed to original StSt or Style
    """
    from coldtype.img.skiaimage import SkiaImage

    def _image_shader(p:P):
        def draw(r, canvas):
            imageShader = image.makeShader(skia.SamplingOptions(skia.FilterMode.kLinear))

            effect = skia.RuntimeEffect.MakeForShader(sksl)

            children = skia.RuntimeEffectChildPtr(imageShader)
            runtime_effect = skia.SpanRuntimeEffectChildPtr(children, 1)
            myShader = effect.makeShader(None, runtime_effect)
            
            paint = skia.Paint()
            paint.setShader(myShader)
            canvas.drawPaint(paint)

        return draw_canvas(r, draw, in_pen=in_pen)
    
    return _image_shader, dict(returns=P if in_pen else SkiaImage)

FREEZES = {}

from inspect import getsource

def freeze(do_freeze, as_image, callback, additionals=[]):
    """
    Use this function to “freeze” the result of another (expensive) function
    as an image, so you don’t have to recompute the same thing over and over

    N.B. Because of a quirk with Python’s introspection facilities, a multi-line
    lambda will work with freeze, but the cache will not update if code changes
    on any line but the first; if you need a multi-line function, pass in a def
    and all the code will be read as a cache key
    """
    def getsrc(f):
        _src = getsource(f)
        if "lambda:" in _src:
            _src = "lambda:".join(_src.split("lambda:")[1:]).strip()
        return _src
    
    src = getsrc(callback)
    for a in additionals:
        if callable(a):
            src += getsrc(a)
        else:
            src += repr(a)

    if not src:
        print("NO SRC FOUND FOR FREEZE")

    if not do_freeze:
        if src in FREEZES:
            del FREEZES[src]
        return callback()
    
    if src in FREEZES:
        currently_image, res = FREEZES[src]
        if as_image != currently_image:
            del FREEZES[src]

    if src not in FREEZES:
        #print("FREEZING", src)
        res = callback()
        if as_image:
            res_img = res.ch(precompose(res.bounds().inset(-100)))
            FREEZES[src] = [1, res_img]
        else:
            FREEZES[src] = [0, res]
    
    return FREEZES[src][-1]