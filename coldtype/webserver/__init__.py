import tempfile, shutil
from urllib.request import urlopen
from coldtype.renderable import renderable
from coldtype.pens.datpen import DATPen, DATPens
from coldtype.pens.skiapen import SkiaPen
from drafting.text.reader import Font, StyledString, Style
from drafting.geometry import Rect
from drafting.color import hsl
from flask import send_file

cottf_path = "https://blog.robstenson.com/assets/ColdtypeObviously-VF.ttf"

with urlopen(cottf_path) as response:
    with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as tf:
        shutil.copyfileobj(response, tf)
        print(tf.name)

cottf = Font(tf.name)

DATPen._pen_class = SkiaPen

@renderable(Rect(1080, 1080), rstate=1)
def test1(r, get):
    f = float(get.get("f", "0.9"))
    txt = get.get("txt", "COLDTYPE")
    return DATPens([
        DATPen(r).f(0),
        DATPen().oval(r.inset(50)).f(hsl(f, 0.75)),
        (StyledString(txt,
            Style(cottf, 500, wdth=0, ro=1, tu=-50, r=1))
            .pens()
            .align(r, tv=1)
            .f(1)
            .understroke(sw=20))
    ])

def hello_world(req):
    rp = test1.passes(None, None)[0]
    result = test1.normalize_result(test1.run(rp, req.args))
    with tempfile.NamedTemporaryFile(suffix="png") as tf:
        SkiaPen.Composite(result, test1.rect, tf.name, context=None)
        return send_file(tf.name, as_attachment=False, attachment_filename="test.png")

if __name__ == "__main__":
    from flask import Flask, request
    app = Flask(__name__)

    @app.route('/')
    def test_hello_world():
        return hello_world(request)
    
    app.run(debug=True)