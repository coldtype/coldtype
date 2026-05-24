from coldtype import *


class config():
    def __call__(self, fn):
        self._data = fn()
        return self

    def data(self, key):
        return self._data[key]["default"]


@config()
def c1():
    return dict(
        letter=dict(default="A", options=["A", "B", "C"]),
        fontSize=dict(default=200, options=range(20, 600)))


@renderable(rect=(1200, 340), bg=0)
def render(r):
    return (StSt(c1.data("letter"), Font.MuSan(), c1.data("fontSize"))
        .align(r)
        .f(1))