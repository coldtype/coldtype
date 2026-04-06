from coldtype import *
import json, os

from pathlib import Path
from base64 import b64encode
from IPython.display import display, SVG, HTML, clear_output
from coldtype.renderable.renderable import renderable as _renderable
from coldtype.renderable.animation import animation as _animation, aframe as _aframe
from coldtype.renderable.animation import Action, Timeline, FFMPEGExport
from coldtype.runon.path import P
from coldtype.pens.svgpen import SVGPen
from coldtype.color import rgb, hsl
from coldtype.geometry import Rect
from subprocess import run
from shutil import rmtree

DEFAULT_DISPLAY = "png"

try:
    from coldtype.fx.skia import precompose
    from coldtype.pens.skiapen import SkiaPen
    from io import BytesIO
except ImportError:
    precompose = None


def update_ffmpeg():
    print("fetching...")
    os.system("add-apt-repository -y ppa:jonathonf/ffmpeg-4")
    print("updating...")
    os.system("apt-get update")
    print("mediainfo...")
    os.system("apt install mediainfo")
    print("ffmpeg...")
    os.system("apt-get install ffmpeg")
    clear_output()
    print('ffmpeg update finished')


def show(fmt="png", rect=None, align=False, padding=[0, 0], tx=0, ty=0, scale=0.5):
    if not precompose and fmt == "png":
        raise Exception("pip install skia-python")
    
    def _display(_pen:P):
        pen = _pen.copy(with_data=1)
        pen.data(_notebook_shown=True)
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
            lar = pen.data("_last_align_rect")
            if lar and False:
                rect = lar
                pen = P([P(rect).fssw(-1, 0.75, 2), pen])
            else:
                amb = pen.ambit(tx=tx, ty=ty)
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
        
        return _pen
    
    return _display


def showpng(rect=None, align=False, padding=[60, 50], tx=0, ty=0, scale=0.5):
    return show("png", rect, align, padding, tx, ty, scale)

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

def show_animation(a:_animation, start=False):
    idxs = range(0, a.duration+1)
    passes = a.passes(Action.PreviewIndices, None, idxs)
    results = [a.run_normal(rp) for rp in passes]
    svg = SVGPen.Animation(results, a.rect, a.timeline.fps)
    html = f"<div id='{a.name}'>{svg}</div>"
    js_call = f"<script type='text/javascript'>{js}; animate('{a.name}', {int(start)})</script>";
    display(HTML(html + js_call), display_id=a.name)

def render_animation(a, show=[], preview_scale=0.5, scale=1):
    try:
        from tqdm.notebook import tqdm
    except (ImportError, ModuleNotFoundError):
        tqdm = None
        print("no tqdm")

    idxs = list(range(0, a.duration))
    passes = a.passes(Action.PreviewIndices, None, idxs)
    output_dir = passes[0].output_path.parent
    if output_dir.exists():
        rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    xs = passes
    if tqdm:
        xs = tqdm(passes, leave=False)

    for idx, rp in enumerate(xs):
        res = a.run_normal(rp)
        if a.fmt == "png":
            SkiaPen.Composite(res, a.rect, str(rp.output_path), scale=scale)
            if show == "*" or idx in show:
                showlocalpng(a.rect, rp.output_path, scale=preview_scale)
        elif a.fmt == "svg":
            SkiaPen.SVG(res, a.rect, str(rp.output_path), scale=scale)
    
    clear_output()

def show_video(a, fmt="h264", loops=1, verbose=False, download=False, scale=0.5, audio=None, audio_loops=None,autoplay=True):
    ffex = FFMPEGExport(a,
        loops=loops,
        audio=audio,
        audio_loops=audio_loops)
    
    if fmt == "h264":
        ffex.h264()
    elif fmt == "gif":
        ffex.gif()
    else:
        print("Unrecognized fmt:", fmt)
        return
    
    ffex.write(verbose=verbose)
    compressed_path = str(ffex.output_path.absolute())

    if fmt == "h264":
        mp4 = open(compressed_path, 'rb').read()
        data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
        clear_output()
        display(HTML(f"""
        <video width={a.rect.w*scale} controls loop=true {'autoplay' if autoplay else ''}>
            <source src="%s" type="video/mp4">
        </video>
        """ % data_url))
    elif fmt == "gif":
        gif = open(compressed_path, 'rb').read()
        data_url = "data:image/gif;base64," + b64encode(gif).decode()
        clear_output()
        #display(HTML(f"<img width={rect.w*scale} src='data:image/gif;base64,{data_url}'/>"))
        display(HTML(f"""<img width={a.rect.w*scale} src="%s"></img>""" % data_url))
    
    if download:
        try:
            from google.colab import files
            files.download(ffex.output_path)
        except ImportError:
            print("download= arg is for colab")
            pass


class notebook_renderable(_renderable):
    def __init__(self,
        rect=(540, 540),
        preview=True,
        preview_scale=0.5,
        render_bg=True,
        border=(0.75, 2),
        **kwargs
        ):
        self._preview = preview
        self.preview_scale = preview_scale
        self.border = border

        super().__init__(rect, render_bg=render_bg, **kwargs)
    
    def __call__(self, func):
        res = super().__call__(func)

        if self._preview:
            self.preview()
        return res
    
    def preview(self):
        res = self.frame_result(0, post=False)
        out = P([
            P(self.rect).fssw(-1, *self.border) if self.border else None,
            res
        ])
        out.ch(show("png", self.rect, padding=[0, 0], scale=self.preview_scale))
        return self


class notebook_animation(_animation):
    def __init__(self,
        rect=(1080, 1080),
        display=True,
        preview_scale=0.5,
        render_bg=True,
        storyboard=None,
        interactive=True,
        render_show=False,
        vars={},
        **kwargs
        ):
        self._display = display
        self.interactive = interactive
        self.preview_scale = preview_scale
        self.render_show = render_show
        self.vars = vars

        if storyboard is None:
            self._storyboarded = False
            storyboard = [0]
        else:
            self.interactive = False
            self._storyboarded = True
        
        self.storyboard = storyboard
        super().__init__(rect, render_bg=render_bg, **kwargs)
    
    def __call__(self, func):
        res = super().__call__(func)
        if self.render_show:
            self.render().show()
        elif self._display:
            self.display()
        return res
    
    def display(self):
        if not self.interactive:
            self.preview(*self.storyboard)
            return

        self._interaction_file = Path("_coldtype_notebook_tmp/" + self.name + "_tmp_state.json")
        self._interaction_state = {}

        if not self._interaction_file.exists():
            self._interaction_file.parent.mkdir(parents=True, exist_ok=True)
            self._interaction_file.write_text("{}")

        if len(self.storyboard) > 1:
            self.preview(*self.storyboard[1:])
        else:
            self.interactive_preview(self.storyboard[0])

    
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
    
    def show(self,
        fmt="h264",
        loops=1,
        verbose=False,
        download=False,
        scale=0.5,
        audio=None,
        audio_loops=None,
        autoplay=True
        ):
        if self.fmt == "svg":
            show_animation(self, start=False)
        else:

            show_video(self,
                fmt=fmt,
                loops=loops,
                verbose=verbose,
                download=download,
                scale=scale,
                audio=audio,
                audio_loops=audio_loops,
                autoplay=autoplay)
        return None
    
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


class notebook_aframe(_aframe):
    def __init__(self,
        rect=(1080, 1080),
        **kwargs
        ):

        super().__init__(rect,
            timeline=Timeline(1),
            interactive=False,
            #storyboard=[0],
            **kwargs)


def nshow(self):
    return self.ch(show(tx=1, ty=1))

P.nshow = nshow

renderable = notebook_renderable
animation = notebook_animation
aframe = notebook_aframe

# to set up font paths correctly (seems fine?)
from coldtype.renderer.reader import SourceReader
NOTEBOOK_SOURCE_READER = SourceReader()
NOTEBOOK_SOURCE_READER.read_configs(None, None)

clear_output()