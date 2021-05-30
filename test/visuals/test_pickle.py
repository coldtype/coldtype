from coldtype import *
import pickle

@renderable(fmt="pickle")
def pickled(r):
    return (DATPen()
        .oval(r.inset(100))
        .f(0)
        .difference(
            DATPen().rect(r.inset(100)).translate(-100, -100))
        .f(hsl(0.5))
        .xor(DATPen().rect(r)))

@renderable()
def unpickle(r):
    try:
        return pickle.load(open("test/renders/test_pickle_pickled.pickle", "rb")).rotate(180)
    except:
        return None
    #return DATPen().oval(r.inset(100))