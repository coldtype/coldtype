from random import Random

def random_series(start=0, end=1, seed=0, count=5000, ease=None):
    from coldtype.timing.easing import ez

    rnd = Random()
    rnd.seed(seed)
    rnds = []
    for _ in range(count):
        e = rnd.random()
        if ease:
            rnds.append(ez(e, ease, rng=(start, end)))
        else:
            rnds.append(start+rnd.random()*(end-start))
    return rnds