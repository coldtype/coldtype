import math
from defcon import Font
from pathlib import Path
import easing_functions as ef
from coldtype.pens.datpen import DATPen
from fontTools.misc.bezierTools import splitCubic, splitLine

from typing import List

eases = dict(
    cei=ef.CubicEaseIn,
    ceo=ef.CubicEaseOut,
    ceio=ef.CubicEaseInOut,
    qei=ef.QuadEaseIn,
    qeo=ef.QuadEaseOut,
    qeio=ef.QuadEaseInOut,
    eei=ef.ExponentialEaseIn,
    eeo=ef.ExponentialEaseOut,
    eeio=ef.ExponentialEaseInOut,
    sei=ef.SineEaseIn,
    seo=ef.SineEaseOut,
    seio=ef.SineEaseInOut,
    bei=ef.BounceEaseIn,
    beo=ef.BounceEaseOut,
    beio=ef.BounceEaseInOut,
    eleo=ef.ElasticEaseOut,
    elei=ef.ElasticEaseIn,
    elieo=ef.ElasticEaseInOut,
    eleio=ef.ElasticEaseInOut)


def curve_pos_and_speed(curve, x):
    x1000 = x*1000
    for idx, (action, pts) in enumerate(curve.value):
        if action in ["moveTo", "endPath", "closePath"]:
            continue
        last_action, last_pts = curve.value[idx-1]
        if action == "curveTo":
            o = -1
            a = last_pts[-1]
            b, c, d = pts
            if x1000 == a[0]:
                o = a[1]/1000
                eb = a
                ec = b
            elif x1000 == d[0]:
                o = d[1]/1000
                eb = c
                ec = d
            elif x1000 > a[0] and x1000 < d[0]:
                e, f = splitCubic(a, b, c, d, x1000, isHorizontal=False)
                ez, ea, eb, ec = e
                o = ec[1]/1000
            else:
                continue
            tangent = math.degrees(math.atan2(ec[1] - eb[1], ec[0] - eb[0]) + math.pi*.5)
            #print(o, tangent)
            if tangent >= 90:
                t = (tangent - 90)/90
            else:
                t = tangent/90
            if o != -1:
                return o, t
    raise Exception("No curve value found!")


def ease(style, x):
    """
    Though available as a general-purpose function, this logic is usually accessed through something like the `.progress` function on an animation or timeable.

    Return two values — the first is the easing result at a given time x; the second is the tangent to that, if calculable (is not, atm, calculable for the mnemonics given)

    for reference, easing mnemonics:

    * cei = CubicEaseIn
    * ceo = CubicEaseOut
    * ceio = CubicEaseInOut
    * qei = QuadEaseIn
    * qeo = QuadEaseOut
    * qeio = QuadEaseInOut
    * eei = ExponentialEaseIn
    * eeo = ExponentialEaseOut
    * eeio = ExponentialEaseInOut
    * sei = SineEaseIn
    * seo = SineEaseOut
    * seio = SineEaseInOut
    * bei = BounceEaseIn
    * beo = BounceEaseOut
    * beio = BounceEaseInOut
    * eleo = ElasticEaseOut
    * elei = ElasticEaseIn,
    * eleio = ElasticEaseInOut
    """
    if style == "linear":
        return x, 0.5
    e = eases.get(style)
    if e:
        return e().ease(x), 0.5
    elif hasattr(style, "moveTo"):
        return curve_pos_and_speed(style, x)
    elif False:
        if style in easer_ufo:
            return curve_pos_and_speed(DATPen().glyph(easer_ufo[style]), x)
        else:
            raise Exception("No easing function with that mnemonic")
    else:
        raise Exception("No easing function with that mnemonic")