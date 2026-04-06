from random import Random

def random_series(start=0, end=1, seed=0, count=5000, ease=None, mod=None, spread=None):
    from coldtype.timing.easing import ez

    rnd = Random()
    rnd.seed(seed)
    rnds = []
    for _ in range(count):
        tries = 0
        while tries < 100:
            e = rnd.random()
            if ease:
                o = ez(e, ease, rng=(start, end))
            else:
                o = start+rnd.random()*(end-start)
            if mod is not None:
                o = mod(o)
            if len(rnds) == 0:
                break
            if spread is None:
                break
            if abs(o-rnds[-1]) > spread:
                break
            tries += 1
        rnds.append(o)
    return rnds