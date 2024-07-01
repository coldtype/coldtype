---
title: "Easing Cheatsheet"
---

In the context of easing, the first letter of an easing mnemonic refers to the type of curve, listed from gentlest to steepest:

* `q` == "quadratic"
* `s` == "sine"
* `c` == "cubic"
* `e` == "exponential"

The ending of a mnemonic refers to the entry/exit of the curve:

* `eio` == "ease-in-out"
* `ei` == "ease-in"
* `eo` == "ease-out"

Put together you get can mnemonics like these:

* `eeio` == "exponential-ease-in-out"
* `ceo` == "cubic-ease-out"
* `sei` == "sine-ease-in"

etc.

Given a frame object ``f`` in an ``@animation`` renderable:

```python
from coldtype import *

@animation(timeline=60) # duration of 60 frames
def easing_example(f):
    square = P(f.a.r.inset(300)).f(0)
    return square.rotate(f.e("eeio", 1, rng=(-10, 10)))
```

In the line ``f.e("eeio", 1, rng=(-10, 10))``, the ``1`` refers to the number of loops, and the ``rng=`` sets a range of values that will be traversed by the easing. By default, this value is rng=(0, 1), so the value would cycle back and forth between 0 and 1 **one-time** (loops=1) over the course of the animation's duration. If you set loops to 0, the value would traverse from 0 to 1 in only one direction and not return to 0 (meaning the value would "pop" back to 0 when the animation itself loops.)