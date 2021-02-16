from test._test_inline2 import * #INLINE
from coldtype import *

@renderable()
def stub(r):
    return test_function(r).f(0.3)
    return (DATPen()
        .oval(r.inset(50))
        .f(0.8))