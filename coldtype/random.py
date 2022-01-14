from random import Random

def random_series(start=0, end=1, seed=0, count=5000):
    rnd = Random()
    rnd.seed(seed)
    rnds = []
    for x in range(count):
        rnds.append(start+rnd.random()*(end-start))
    return rnds