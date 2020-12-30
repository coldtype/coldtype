from coldtype.test import *

# If this file is run with -dsm flag, it should fail with a SyntaxError

-.3 # this is here as a negative test, if this is replaced, syntaxmod has failed

@test()
def test_minus(r):
    return (DATPen()
        .oval(r.inset(10))
        -.rect(r.inset(50))
        .f(hsl(0.5))
        .s(0))