import skia, tempfile
from subprocess import run
from functools import reduce
from random import Random, randint
from pathlib import Path

from fontTools.svgLib import SVGPath
from fontTools.misc.transform import Transform

from coldtype.color import normalize_color, bw
from coldtype.pens.skiapen import SkiaPen
from coldtype.pens.datpen import DATPen

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

        return skia.BlurImageFilter.Make(xblur, yblur)

    @staticmethod
    def improved_noise(e, xo=0, yo=0, xs=1, ys=1, base=1):
        noise = skia.PerlinNoiseShader.MakeImprovedNoise(0.015, 0.015, 3, base)
        matrix = skia.Matrix()
        matrix.setTranslate(e*xo, e*yo)
        #matrix.setRotate(45, 0, 0)
        matrix.setScaleX(xs)
        matrix.setScaleY(ys)
        return noise.makeWithLocalMatrix(matrix)


# CHAINABLES

def spackle(xo=None, yo=None,
    xs=0.85, ys=0.85, base=None,
    cut=240, cutw=5
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
                        Skfi.fill(bw(1)),
                        Skfi.as_filter(Skfi.contrast_cut(cut, cutw)),
                        skia.LumaColorFilter.Make()))))))
    return _spackle


def fill(c):
    c = normalize_color(c)
    def _fill(pen):
        return pen.attr(skp=dict(
            ColorFilter=Skfi.fill(c)))
    return _fill


def potrace(rect, poargs=[], invert=True):
    from PIL import Image

    pc = SkiaPen
    ctx = SKIA_CONTEXT

    def _potrace(pen):
        img = pc.Precompose(pen, rect, context=ctx)
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
            if False:
                print(result)
            t = Transform()
            t = t.scale(0.1, 0.1)
            svgp = SVGPath.fromstring(result.stdout, transform=t)
            if False:
                print(svgp)
            dp = DATPen()
            svgp.draw(dp)
            return dp.f(0)
    return _potrace


def precompose(rect,
    placement=None,
    opacity=1,
    scale=1
    ):
    def _precompose(pen):
        img = SkiaPen.Precompose(pen, rect,             
            context=SKIA_CONTEXT,
            scale=scale,
            disk=False)    
        return (DATPen()
            .rect(placement or rect)
            .img(img, (placement or rect), False, opacity)
            .f(None))
    return _precompose


def rasterized(rect, scale=1):
    """
    Same as precompose but returns the Image created rather
    than setting that image as the attr-image of this pen
    """
    def _rasterized(pen):
        return SkiaPen.Precompose(pen, rect, scale=scale, context=SKIA_CONTEXT, disk=False)
    return _rasterized, dict(returns=skia.Image)


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
        return (DATPen()
            .rect(rect)
            .img(out, rect, False)
            .f(None))
    
    return _mod_pixels


def phototype(rect,
    blur=5,
    cut=127,
    cutw=3,
    fill=1,
    rgba=[0, 0, 0, 1],
    luma=True
    ):
    def _phototype(pen):
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
    return _phototype


def color_phototype(rect,
    blur=5,
    cut=127,
    cutw=15,
    rgba=[1, 1, 1, 1]
    ):
    return phototype(rect, blur, 255-cut, cutw, fill=None, rgba=rgba, luma=False)