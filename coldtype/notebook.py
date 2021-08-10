from pathlib import Path
from IPython.display import display, SVG, Image, HTML
from coldtype.renderable.animation import animation, Action
from coldtype.pens.svgpen import SVGPen
from coldtype.geometry import Rect

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
            display(src)
        elif fmt == "svg":
            svg = SVGPen.Composite(pen, rect, viewBox=False)
            #print(svg)
            display(SVG(svg))
        return pen
    
    return _display

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
    a.output_folder = Path(".")
    idxs = range(0, a.duration+1)
    passes = a.passes(Action.PreviewIndices, None, idxs)
    results = [a.run_normal(rp) for rp in passes]
    svg = SVGPen.Animation(results, a.rect, a.timeline.fps)
    html = f"<div id='{a.name}'>{svg}</div>"
    js_call = f"<script type='text/javascript'>{js}; animate('{a.name}', {int(start)})</script>";
    display(HTML(html + js_call), display_id=a.name)