from pathlib import Path
from base64 import b64encode
from IPython.display import display, SVG, Image, HTML
from coldtype.renderable.animation import animation, Action
from coldtype.pens.svgpen import SVGPen
from coldtype.geometry import Rect

try:
    from coldtype.fx.skia import precompose, skia
    from coldtype.pens.skiapen import SkiaPen
    from PIL import Image
    from io import BytesIO
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
            with BytesIO(src.encodeToData()) as f:
                f.seek(0)  # necessary?
                b64 = b64encode(f.read()).decode("utf-8")
                display(HTML(f"<img width={rect.w/2} src='data:image/png;base64,{b64}'/>"))
        elif fmt == "svg":
            svg = SVGPen.Composite(pen, rect, viewBox=False)
            display(SVG(svg))
        return pen
    
    return _display


def showpng(rect=None, align=False, padding=[60, 50], th=0, tv=0):
    return show("img", rect, align, padding, th, tv)

def showlocalpng(rect, src):
    with open(src, "rb") as img_file:
        encoded_string = b64encode(img_file.read()).decode("utf-8")
        display(HTML(f"<img width={rect.w/2} src='data:image/png;base64,{encoded_string}'/>"))

def showframe(a, idx):
    rp = a.passes(Action.PreviewIndices, None, [idx])[0]
    res = a.run_normal(rp)
    rp.output_path.parent.mkdir(parents=True, exist_ok=True)
    SkiaPen.Composite(res, a.rect, str(rp.output_path))
    showlocalpng(a.rect, rp.output_path)


js = """
function animate(name, start_playing) {
    svg = document.querySelector(`#${name} svg`);
    svg_frames = [].slice.apply(svg.querySelectorAll(".frame"));
    svg_frames.forEach((sf) => sf.style.display = "none");
    svg_frames[0].style.display = "block";

    var fps = parseFloat(svg.dataset.fps);
    var duration = parseInt(svg.dataset.duration);
    var fpsInterval = 1000 / fps;
    var then = Date.now();
    var startTime = then;
    var elapsed = 0;
    var i = 0;
    var playing = !!start_playing;

    function _animate() {
        if (!playing) {
            return;
        }
        requestAnimationFrame(_animate);
        var now = Date.now();
        elapsed = now - then;
        if (elapsed > fpsInterval) {
            then = now - (elapsed % fpsInterval);
            svg_frames.forEach((sf) => sf.style.display = "none");
            svg_frames[i%duration].style.display = "block";
            i++;
        }
    }

    svg.addEventListener("click", function() {
        if (playing) {
            playing = false;
        } else {
            playing = true;
            _animate();
        }
    });

    if (playing) {
        _animate();
    }
}
"""

def show_animation(a:animation, start=False):
    idxs = range(0, a.duration+1)
    passes = a.passes(Action.PreviewIndices, None, idxs)
    results = [a.run_normal(rp) for rp in passes]
    svg = SVGPen.Animation(results, a.rect, a.timeline.fps)
    html = f"<div id='{a.name}'>{svg}</div>"
    js_call = f"<script type='text/javascript'>{js}; animate('{a.name}', {int(start)})</script>";
    display(HTML(html + js_call), display_id=a.name)

def render_animation(a):
    idxs = list(range(0, a.duration+1))
    passes = a.passes(Action.PreviewIndices, None, idxs)
    passes[0].output_path.parent.mkdir(parents=True, exist_ok=True)
    for rp in passes:
        res = a.run_normal(rp)
        SkiaPen.Composite(res, a.rect, str(rp.output_path))
        showlocalpng(a.rect, rp.output_path)