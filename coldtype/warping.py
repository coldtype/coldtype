import noise


def warp_fn(xa=0, ya=-1, xs=300, ys=300, speed=5, base=0, octaves=1, mult=50, rz=1024):
    if ya == -1:
        ya = xa
    def warp(x, y):
        _x = (x+xa)/xs
        _y = (y+ya)/ys
        pn = noise.pnoise3(_x, _y, speed, octaves=octaves, base=base, repeatz=rz)
        return x+pn*mult, y+pn*mult
    return warp