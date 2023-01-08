import inspect, jinja2, markdown
from collections import namedtuple

from coldtype import *
from coldtype.runon import Runon

from time import time
from textwrap import dedent
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from lxml.html import fragment_fromstring, tostring

classes = [
    P,
    Style,
    Rect,
    Scaffold,
    Runon,
]

decorators = [
    renderable,
    animation,
]

functions = [
    StSt,
    Glyphwise
]

root = Path("./coldtype").resolve()

output = {
    "decorators": [],
    "classes": [],
    "functions": [],
}

doc = namedtuple("doc", ["itself", "path", "docstring", "signature", "methods"])

for k, v in output.items():
    for x in globals()[k]:
        docstring = inspect.getdoc(x)
        if docstring:
            docstring_md = markdown.markdown(docstring, extensions=["smarty", "mdx_linkify", "fenced_code", "codehilite"], extension_configs={"codehilite":{"css_class":"highlight"}})
            path = Path(inspect.getfile(x)).relative_to(root)
            sig = None
            src = None
            methods = []

            if inspect.isclass(x):
                src = inspect.getsource(getattr(x, "__init__"))
                src = dedent(f"class {x.__name__}:\n" + src.split("):")[0] + "):")
                
                _methods = inspect.getmembers(x)
                for m in _methods:
                    try:
                        _path = Path(inspect.getfile(m[1])).relative_to(root)
                    except TypeError:
                        _path = None
                    
                    if _path == path and m[1].__name__ not in ["__init__", "__call__", "__repr__", "__eq__"]:
                        ds = inspect.getdoc(m[1])
                        if ds:
                            ds_md = markdown.markdown(ds, extensions=["smarty", "mdx_linkify", "fenced_code", "codehilite"], extension_configs={"codehilite":{"css_class":"highlight"}})
                            _src = dedent(inspect.getsource(m[1]).split("->")[0])
                            _highlit = fragment_fromstring(highlight(_src, PythonLexer(), HtmlFormatter(linenos=False)))
                            _sig = tostring(_highlit, pretty_print=True, encoding="utf-8").decode("utf-8")
                            methods.append(doc(m[1], path, ds_md, _sig, None))
                
                methods = sorted([*set(methods)], key=lambda m: m.itself.__name__)

            else:
                src = dedent(inspect.getsource(x).split("->")[0])
            
            if src:
                highlit = fragment_fromstring(highlight(src, PythonLexer(), HtmlFormatter(linenos=False)))
                sig = tostring(highlit, pretty_print=True, encoding="utf-8").decode("utf-8")

            output[k].append(doc(x.__name__, path, docstring_md, sig, methods))
        
        #if inspect.isclass(x):
        #    print(path, k, inspect.isclass(x))


here = Path(__FILE__).parent.resolve()
build_dir = here / "site"
template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(here / "templates")))
docs_template = template_env.get_template("docs.j2")

(build_dir / "classes_functions.html").write_text(docs_template.render(dict(docs=output, build_unix=int(time()))))

@renderable((100, 100), watch=[here / "templates/docs.j2"])
def a(r):
    return None