import json

from pathlib import Path
from base64 import b64encode
from IPython.display import display, SVG, HTML
from coldtype.renderable.animation import aframe, animation, Action, Timeline
from coldtype.pens.svgpen import SVGPen
from coldtype.geometry import Rect
from coldtype.renderable.animation import FFMPEGExport
from subprocess import run
from shutil import rmtree


try:
    from coldtype.fx.skia import precompose
    from coldtype.pens.skiapen import SkiaPen
    from io import BytesIO
except ImportError:
    precompose = None


def show(fmt=None, rect=None, align=False, padding=[60, 50], th=0, tv=0, scale=0.5):
    if not precompose and fmt == "png":
        raise Exception("pip install skia-python")
    
    def _display(pen):
        nonlocal rect, fmt

        if fmt is None:
            img = pen.img()
            if img and img.get("src"):
                fmt = "png"
            else:
                fmt = "svg"

        if align and rect is not None:
            pen.align(rect)
        if rect is None:
            amb = pen.ambit(th=th, tv=tv)
            rect = Rect(amb.w+padding[0], amb.h+padding[1])
            pen.align(rect)
        
        if fmt == "png":
            src = pen.ch(precompose(rect)).img().get("src")
            with BytesIO(src.encodeToData()) as f:
                f.seek(0)  # necessary?
                b64 = b64encode(f.read()).decode("utf-8")
                display(HTML(f"<img width={rect.w*scale} src='data:image/png;base64,{b64}'/>"))
        elif fmt == "svg":
            svg = SVGPen.Composite(pen, rect, viewBox=False)
            display(SVG(svg))
        return pen
    
    return _display


def showpng(rect=None, align=False, padding=[60, 50], th=0, tv=0, scale=0.5):
    return show("png", rect, align, padding, th, tv, scale)

def showlocalpng(rect, src, scale=0.5):
    with open(src, "rb") as img_file:
        encoded_string = b64encode(img_file.read()).decode("utf-8")
        display(HTML(f"<img width={rect.w*scale} src='data:image/png;base64,{encoded_string}'/>"))

def show_frame(a, idx, scale=0.5):
    rp = a.passes(Action.PreviewIndices, None, [idx])[0]
    res = a.run_normal(rp)
    show(a.fmt, a.rect, padding=[0, 0], scale=scale)(res)
    #rp.output_path.parent.mkdir(parents=True, exist_ok=True)
    #SkiaPen.Composite(res, a.rect, str(rp.output_path))
    #showlocalpng(a.rect, rp.output_path)


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

def render_animation(a, show=[], preview_scale=0.5, scale=1):
    from tqdm.notebook import tqdm

    idxs = list(range(0, a.duration))
    passes = a.passes(Action.PreviewIndices, None, idxs)
    output_dir = passes[0].output_path.parent
    if output_dir.exists():
        rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx, rp in enumerate(tqdm(passes, leave=False)):
        res = a.run_normal(rp)
        if a.fmt == "png":
            SkiaPen.Composite(res, a.rect, str(rp.output_path), scale=scale)
            if show == "*" or idx in show:
                showlocalpng(a.rect, rp.output_path, scale=preview_scale)
        elif a.fmt == "svg":
            SkiaPen.SVG(res, a.rect, str(rp.output_path), scale=scale)

def show_video(a, loops=1, verbose=False, download=False, scale=0.5):
    ffex = FFMPEGExport(a, loops=loops)
    ffex.h264()
    ffex.write(verbose=verbose)
    compressed_path = str(ffex.output_path.absolute())
    mp4 = open(compressed_path, 'rb').read()
    data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
    display(HTML(f"""
    <video width={a.rect.w*scale} controls loop=true autoplay>
        <source src="%s" type="video/mp4">
    </video>
    """ % data_url))
    if download:
        try:
            from google.colab import files
            files.download(ffex.output_path)
        except ImportError:
            print("download= arg is for colab")
            pass


class notebook_animation(animation):
    def __init__(self,
        rect=(540, 540),
        preview=[0],
        interactive=True,
        preview_scale=0.5,
        render_bg=True,
        vars={},
        **kwargs
        ):
        self._preview = preview
        self._interactive = interactive
        self.preview_scale = preview_scale
        self.vars = vars

        super().__init__(rect, render_bg=render_bg, **kwargs)
    
    def __call__(self, func):
        res = super().__call__(func)

        self._interaction_file = Path(self.name + "_tmp_state.json")
        self._interaction_state = {}

        if self._preview:
            if self._interactive:
                if not self._interaction_file.exists():
                    self._interaction_file.write_text("{}")
                self.interactive_preview(self._preview[0])
            else:
                self.preview(*self._preview)
        return res
    
    def interactive_preview(self, start):
        from ipywidgets import IntSlider, FloatSlider, interact
        self._interaction_state = json.loads(self._interaction_file.read_text())

        def show_anim(**kwargs):
            self._interaction_state = kwargs
            self._interaction_file.write_text(json.dumps(kwargs))
            self.preview(kwargs["i"])

        vars = dict(i=IntSlider(
            min=0,
            max=self.duration-1,
            continuous_update=False,
            value=self._interaction_state.get("i", 0),
            description="f.i"))
    
        for v, val in self.vars.items():
            vars[v] = FloatSlider(min=0,
                max=1, step=1e-2,
                continuous_update=False,
                value=self._interaction_state.get(v, val))
        
        interact(show_anim, **vars)
    
    def iv(self, k):
        return self._interaction_state.get(k, 0)
    
    def preview(self, *frames):
        if len(frames) == 0:
            frames = [0]
        elif len(frames) == 1:
            if frames[0] == "*":
                frames = list(range(self.start, self.end))
        
        for frame in frames:
            show_frame(self, frame, scale=self.preview_scale)
        return self
    
    def render(self, scale=1):
        render_animation(self, show=[], scale=scale)
        return self
    
    def show(self, loops=1, verbose=False, download=False, scale=0.5):
        if self.fmt == "svg":
            show_animation(self, start=False)
        else:
            show_video(self, loops=loops, verbose=verbose, download=download, scale=scale)
        return self
    
    def zip(self, download=False):
        zipfile = f"{str(self.output_folder)}.zip"
        run(["zip", "-j", "-r", zipfile, str(self.output_folder)])
        print("> zipped:", zipfile)
        if download:
            try:
                from google.colab import files
                files.download(zipfile)
            except ImportError:
                print("download= arg is for colab")
                pass
        return self


class notebook_aframe(aframe):
    def __init__(self,
        rect=(540, 540),
        **kwargs
        ):
        self._preview = [0]

        super().__init__(rect,
            timeline=Timeline(1),
            interactive=False,
            **kwargs)