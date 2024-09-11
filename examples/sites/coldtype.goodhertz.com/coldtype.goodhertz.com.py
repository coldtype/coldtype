from coldtype import *
from coldtype.web.site import *
from functools import partial

import inspect, markdown

from time import time
from textwrap import dedent
from coldtype.runon import Runon
from collections import namedtuple

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from lxml.html import fragment_fromstring, tostring

classes = [ P, Style, Rect, Scaffold, Runon ]

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

def classes_functions(s:site):
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
                        except (TypeError, ValueError):
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

    page = Page(None, None, f"classes_functions.html", "Classes & Functions", "_docs", None, None, None, None)
    s.render_page(page, dict(docs=output))
    return page

hierarchy = {
    "mains": ["introduction.html", "about.html", "overview.html", "install.html", "classes_functions.html"],
    "tutorials": ["tutorials/shapes.html", "tutorials/geometry.html", "tutorials/text.html", "tutorials/animation.html", "tutorials/drawbot.html", "tutorials/blender.html"],
    "cheatsheets": ["cheatsheets/viewer.html", "cheatsheets/easing.html", "cheatsheets/rectangles.html", "cheatsheets/oneletter.html", "cheatsheets/text.html"],
}

def section(section, site):
    return sorted([p for p in site.pages if p.slug in hierarchy[section]], key=lambda p: hierarchy[section].index(p.slug))

info = dict(
    title="Coldtype Tutorials",
    description="These are Coldtype tutorials",
    navigation={
        #"Home": "/",
        #"About": "/about"
        "coldtype.xyz": "https://coldtype.xyz/",
        "blog": "https://blog.coldtype.xyz/",
        "github": "https://github.com/coldtype",
        "youtube": "https://www.youtube.com/channel/UCIRaiGAVFaM-pSErJG1UZFA",
        "q&a forum": "https://github.com/goodhertz/coldtype/discussions",
    })

@site(ººsiblingºº(".")
    , port=8008
    , sources=dict(
        mains=partial(section, "mains"),
        tutorials=partial(section, "tutorials"),
        cheatsheets=partial(section, "cheatsheets"))
    , generators=dict(
        classes_functions=classes_functions)
    , info=info
    , template=lambda _: "_page"
    , slugs="nested,html"
    , fonts={
        "text-font": dict(regular="MDSystem-VF"),
        "mono-font": dict(regular="MDIO-VF")})
def website(_):
    website.build()

def release(_):
    website.upload("coldtype.goodhertz.com", "us-east-1", None)