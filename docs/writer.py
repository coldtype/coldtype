import inspect
from collections import namedtuple
from coldtype import *
from coldtype.runon import Runon

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

doc = namedtuple("doc", ["itself", "path", "docstring"])

for k, v in output.items():
    for x in globals()[k]:
        docstring = inspect.getdoc(x)
        path = Path(inspect.getfile(x)).relative_to(root)
        output[k].append(doc(x, path, docstring))
        
        #if inspect.isclass(x):
        #    print(path, k, inspect.isclass(x))

# for c in classes:
#     docstring = inspect.getdoc(c)
#     path = Path(inspect.getfile(c)).relative_to(root)

# for f in functions:
#     docstring = inspect.getdoc(f)
#     path = Path(inspect.getfile(f)).relative_to(root)