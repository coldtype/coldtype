from IPython.display import display, SVG, Image
from coldtype.geometry import Rect
from coldtype.pens.svgpen import SVGPen

try:
    from coldtype.fx.skia import precompose, skia
    import PIL.Image
except ImportError:
    precompose = None


def show(fmt=None, rect=None, align=False, padding=[60, 50], th=0, tv=0):
    if not precompose and fmt == "img":
        raise Exception("pip install skia-python")
    
    def _display(pen):
        nonlocal rect, fmt

        if fmt is None:
            img = pen.img()
            if img and img.get("src"):
                fmt = "img"
            else:
                fmt = "svg"

        if align and rect is not None:
            pen.align(rect)
        if rect is None:
            amb = pen.ambit(th=th, tv=tv)
            rect = Rect(amb.w+padding[0], amb.h+padding[1])
            pen.align(rect)
        
        if fmt == "img":
            src = pen.ch(precompose(rect)).img().get("src")
            pil_img = PIL.Image.fromarray(src.convert(alphaType=skia.kUnpremul_AlphaType))
            display(Image(pil_img.convert('RGBX').tobytes()))
        elif fmt == "svg":
            svg = SVGPen.Composite(pen, rect, viewBox=False)
            #print(svg)
            display(SVG(svg))
        return pen
    
    return _display