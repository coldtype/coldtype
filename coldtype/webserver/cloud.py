import tempfile, shutil
from urllib.request import urlopen
from coldtype.renderable import renderable
from coldtype.webserver.cdelopty import evalcdel
from coldtype.pens.datpen import DATPen, DATPens
from coldtype.pens.skiapen import SkiaPen
from coldtype.text.reader import Font #, StyledString, Style
from coldtype.geometry import Rect
from coldtype.color import hsl
from flask import send_file

cottf_path = "https://blog.robstenson.com/assets/ColdtypeObviously-VF.ttf"

with urlopen(cottf_path) as response:
    with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as tf:
        shutil.copyfileobj(response, tf)
        print(tf.name)

cottf = Font(tf.name)
fonts = {"co": cottf}

test = [
    ["P", "®", ".", ["f", 0]],
    ["P", ".",
        ["oval", ["R", "®", ".", ["inset", 50]]],
        ["f", ["hsl", 0.6, {"s":1}]],
        ["align", "®"]],
    ["S", "COLD", "co", 500,
        {"wdth":0.5, "tu":-80, "r":1, "ro": 1, "rotate":-5},
        ".",
        ["pens"],
        ["align", "®"],
        ["f", 1],
        ["understroke", 0, 30],
        ["rotate", 15]]]

DATPen._pen_class = SkiaPen

@renderable(Rect(1080, 1080), rstate=1)
def test1(r, get):
    return evalcdel(get.get("cdel", test), r, fonts)

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