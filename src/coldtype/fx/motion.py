from noise import pnoise1


def filmjitter(doneness, base=0, speed=(10, 20), scale=(2, 3), octaves=16):
    """
    An easy way to make something move in a way reminiscent of misregistered film
    """
    def _filmjitter(pen):
        nx = pnoise1(doneness*speed[0], base=base, octaves=octaves)
        ny = pnoise1(doneness*speed[1], base=base+10, octaves=octaves)
        return pen.translate(nx * scale[0], ny * scale[1])
    return _filmjitter