

def midi_controller_lookup_fn(name, column_starts=[], cmc={}):
    """
    Intuitive lookup function generator for midi controls
    scheme is bottom-to-top, 10 is equivalent to column 1, row 0
    22 == column 2, row 3, etc. (or can be customized for
    whatever device you’d like)
    """
    # TODO use the name so individual devices are targetable
    def lookup(ctrl, default=0.5):
        column = int(str(ctrl)[0])
        row = int(str(ctrl)[1])
        mnum = column_starts[row]+(column-1)
        return cmc.get(mnum, default)
    return lookup


def LaunchControlXL(cmc):
    lookup = midi_controller_lookup_fn(
        "Launch Control XL",
        column_starts=[77, 49, 29, 13],
        cmc=cmc)
    
    return (lookup, dict(
        fontSize=lookup(10)*2000+10,
        wdth=lookup(11),
        wght=lookup(21),
        slnt=lookup(31),
        tu=lookup(20)*500-250,))