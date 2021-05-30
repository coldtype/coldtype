from coldtype.test import *

# If this file is run with -dsm flag, it should fail with a SyntaxError

-.3 # this is here as a negative test, if this is replaced, syntaxmod has failed

@test()
def test_minus(r):
    return (DATPen()
        .oval(r.inset(10))
        -.rect(
            r.inset(50))
        -.cool(
            1, ((((((1)))))))
        .f(hsl(0.5))
        .s(0))

@test()
def test_Ƨ(r):
    return DATPens([
        (DP(r.inset(100)).f(hsl(0.3))),
        Ƨ(DP(r.inset(50).t(0, 150)).f(hsl(0.1))),
    ])

# import regex
import inspect
source_code = inspect.getsource(test_minus.func)
assert(source_code.count(".noop(") == 2)
print(source_code)

source_code = inspect.getsource(test_Ƨ.func)
assert(source_code.count("noop(") == 1)
print(source_code)