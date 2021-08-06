

def midi_controller_lookup_fn(name, column_starts=[], cmc={}, channel="9"):
    """
    Intuitive lookup function generator for midi controls
    scheme is bottom-to-top, 10 is equivalent to column 1, row 0
    22 == column 2, row 3, etc. (or can be customized for
    whatever device you’d like)
    """
    # TODO use the name so individual devices are targetable
    def lookup(ctrl, default=None):
        scoped = cmc.get(name, {})
        scoped = scoped.get(str(channel), {})
        if column_starts:
            column = int(str(ctrl)[0])
            row = int(str(ctrl)[1])
            mnum = column_starts[row]+(column-1)
        else:
            mnum = ctrl
        return scoped.get(str(mnum), 63.5 if default == None else default*127) / 127
    return lookup


def Generic(name, cmc, channel):
    return midi_controller_lookup_fn(name, cmc=cmc, channel=channel)


def LaunchControlXL(cmc, channel="9"):
    return midi_controller_lookup_fn(
        "Launch Control XL",
        column_starts=[77, 49, 29, 13],
        cmc=cmc,
        channel=channel)


def LaunchkeyMini(cmc, channel="9"):
    return midi_controller_lookup_fn(
        "Launchkey Mini LK Mini MIDI",
        column_starts=[21],
        cmc=cmc,
        channel=channel)