import inspect
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
print(root)

for d in decorators:
    docstring = inspect.getdoc(d)
    path = Path(inspect.getfile(d)).relative_to(root)

for c in classes:
    docstring = inspect.getdoc(c)
    path = Path(inspect.getfile(c)).relative_to(root)

for f in functions:
    docstring = inspect.getdoc(f)
    path = Path(inspect.getfile(f)).relative_to(root)