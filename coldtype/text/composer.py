from coldtype.runon.path import P
from coldtype.geometry import Rect, Point

from coldtype.text.shaper import segment
from coldtype.text.reader import Style, StyledString, FittableMixin, Font, SegmentedString

import inspect
from collections import namedtuple

class GrafStyle():
    def __init__(self, leading=10, x="centerx", xp=0, width=0, **kwargs):
        self.leading = kwargs.get("l", leading)
        self.x = x
        self.xp = xp
        self.width = width


class Graf():
    def __init__(self, lines, container, style=None, no_frames=False, **kwargs):
        if isinstance(container, Rect):
            self.container = P().rect(container)
        else:
            self.container = container
        if style and isinstance(style, GrafStyle):
            self.style = style
        elif style and isinstance(style, int):
            self.style = GrafStyle(leading=style)
        else:
            self.style = GrafStyle(**kwargs)
        
        self.no_frames = no_frames
        self.lines = lines
    
    def lineRects(self):
        # which came first, the height or the width???
        rects = []
        leadings = []
        box = self.container.ambit()
        leftover = box
        for l in self.lines:
            box, leftover = leftover.divide(l.height(), "maxy", forcePixel=True)
            if self.style.leading < 0:
                # need to add pixels back to leftover
                leftover.h += abs(self.style.leading)
            else:
                leading, leftover = leftover.divide(self.style.leading, "maxy", forcePixel=True)
                leadings.append(leading)
            rects.append(box)
        return rects
    
    def width(self):
        if self.style.width > 0:
            return self.style.width
        else:
            return max([l.width() for l in self.lines])

    def fit(self, width=None):
        rects = self.lineRects()
        for idx, l in enumerate(self.lines):
            if width:
                fw = width
            else:
                fw = rects[idx].w - self.style.xp
            l.fit(fw)
        return self
    
    def pens(self):
        rects = self.lineRects()
        pens = P()
        for idx, l in enumerate(self.lines):
            r = rects[idx]
            dps = l.pens().translate(r.x, r.y) # r.x
            if not self.no_frames:
                dps.data(frame=Rect(r.x, r.y, r.w, r.h))
            pens.append(dps)
        return pens


class Lockup(FittableMixin):
    def __init__(self, slugs, preserveLetters=True, nestSlugs=True):
        self.slugs = slugs
        self.preserveLetters = preserveLetters
        self.nestSlugs = nestSlugs
    
    def width(self):
        return sum([s.width() for s in self.slugs])
    
    def height(self):
        return max([s.height() for s in self.slugs])
    
    def textContent(self):
        return "/".join([s.textContent() for s in self.slugs])

    def shrink(self):
        adjusted = False
        for s in self.slugs:
            adjusted = s.shrink() or adjusted
        return adjusted

    def pens(self):
        pens = []
        x_off = 0
        for s in self.slugs:
            try:
                x_off += s.margin[0]
            except:
                pass
            if self.preserveLetters:
                dps = s.pens()
                dps.translate(x_off, 0)
                if self.nestSlugs:
                    pens.append(dps)
                else:
                    pens.extend(dps._els)
            else:
                dps = s.pen()
                dps.translate(x_off, 0)
                pens.append(dps)
            x_off += dps.ambit(th=0).w
            try:
                x_off += s.margin[1]
                x_off += s.strings[-1].tracking
            except:
                pass
        return P(pens)
    
    def pen(self):
        return self.pens().pen()
    
    def TextToLines(text, primary, fallback=None):
        lines = []
        for line in text.split("\n"):
            lines.append(Lockup([Slug(line, primary, fallback)]))
        return lines
    
    def SlugsToLines(slugs):
        return [Lockup([slug]) for slug in slugs]


def T2L(text, primary, fallback=None):
    return Lockup.TextToLines(text, primary, fallback)


class Slug(SegmentedString):
    def __init__(self, text, primary, fallback=None):
        self.text = text
        self.primary = primary
        self.fallback = fallback
        self.strings = []
        self.tag()
    
    def tag(self):
        if self.fallback:
            segments = segment(self.text, "LATIN")
            self.strings = [StyledString(s[1], self.fallback if "LATIN" in s[0] else self.primary) for s in segments]
        else:
            self.strings = [StyledString(self.text, self.primary)]
    
    def pen(self):
        return self.pens().pen()
    
    def LineSlugs(text, primary, fallback=None):
        lines = []
        for line in text.split("\n"):
            lines.append(Slug(line, primary, fallback))
        return lines


class Composer():
    """
    For multiline text lockups
    """
    def __init__(self, rect:Rect, text:str, style:Style, leading=10, fit=None):
        lockups = Slug.LineSlugs(text, style)
        self.rect = rect
        self.graf = Graf(lockups, self.rect, leading=leading)
        if fit is not None:
            self.graf.fit(fit)
    
    def pens(self):
        """
        Structured representation of the multi-line text
        
        In the result, each line will be a ``P``, then within those lines, each glyph/ligature for that line will be an individual ``P``
        """
        return self.graf.pens()
    
    def pen(self):
        """
        Entire multiline text as a single vector
        """
        return self.graf.pens().pen()


def StSt(text,
    font,
    font_size=24,
    rect=Rect(1080, 1080),
    strip=True,
    multiline=False,
    #xa="mdx",
    **kwargs) -> P:

    if not isinstance(text, str):
        text = "\n".join(text)
    else:
        if strip:
            text = text.strip()
    
    if isinstance(font, Style):
        style = font
    elif isinstance(font, dict):
        style = Style(**{**font, **kwargs})
    else:
        style = Style(font, font_size, **kwargs)
    
    fit = kwargs.get("fit", None)
    leading = kwargs.get("leading", 10)

    if "\n" in text:
        lines = P()
        for l in text.split("\n"):
            lines.append(StSt(l, font, font_size, rect=rect, strip=strip, **{**kwargs, **dict(multline=False)}))
        return lines.stack(leading)
    else:
        if style.fallback:
            lockup = Slug(text, style, style.fallback)
            if fit:
                lockup.fit(fit)
            lockup = lockup.pens(flat=False)
        else:
            lockup = StyledString(text, style)
            if fit:
                lockup.fit(fit)
            lockup = lockup.pens()
        
        if multiline:
            return P([lockup])

        #lockup._stst_style = style
        return lockup


GlyphwiseGlyph = namedtuple("GlyphwiseGlyph", ["i", "c", "e", "l", "li"])


def Glyphwise(st, styler, start=0, line=0, multiline=False):
    # TODO possible to have an implementation
    # aware of a non-1-to-1 mapping of characters
    # to glyphs? seems very difficult if not impossible,
    # since it requires mapping the string to glyphs
    # and then somehow mapping the glyphs back to the
    # equivalent string (?) in order to get the proper
    # kerning information for the sub-strings —
    # it maybe possible to pass glyph-id's directly
    # to harfbuzz, which would solve the problem,
    # though that does seem kind of hard to believe

    #glyphs = StyledString(st, styler(0, st[0])).glyphs
    #print(glyphs)
    #print([g.name for g in glyphs])

    def except_reverse():
        raise Exception("r=1 not possible in a Glyphwise; please use a .reversePens() after the Glyphwise constructor")

    def run_styler(g):
        styles = styler(g)
        if isinstance(styles, Style):
            if styles.reverse:
                except_reverse()
            return styles, None
        else:
            if isinstance(styles[1], dict):
                if styles[0].reverse:
                    except_reverse()
                return styles[0], styles[0].mod(**styles[1])
            else:
                if styles[0].reverse:
                    except_reverse()
                return styles

    if len(st) == 1:
        return StSt(st,
            run_styler(
                GlyphwiseGlyph(0, st, 0, line, 0))[0], strip=False)

    try:
        lines = st.split("\n")
        if len(lines) > 1 or multiline:
            gs = []
            start = 0
            for lidx, l in enumerate(lines):
                gs.append(Glyphwise(l, styler, start=start, line=lidx))
                start += len(l)
            return P(gs).stack()
    except AttributeError:
        pass

    def kx(dps, idx):
        return dps[idx].ambit().x
    
    def krn(off, on, idx):
        return kx(off, idx) - kx(on, idx)

    dps = P()
    prev = 0
    tracks = []

    for idx, c in enumerate(st):
        #c = gi.name
        test = c
        target = 0
        tcount = 1
        if idx < len(st) - 1:
            test = [test, st[idx+1]]
            tcount += 1
        if idx > 0:
            test = [st[idx-1], test]
            target = 1
            tcount += 1
        if isinstance(test, str):
            test = [test]
        
        e = idx / (len(st)-1)
        gg = GlyphwiseGlyph(idx+start, c, e, line, idx)

        skon, skon_tweak = run_styler(gg)
        skoff = skon.mod(kern=0, kern_pairs={}, kp={}, tu=0)

        #test_list = [t for sublist in test for t in sublist]
        #print(test_list)
        test_str = "".join([t if isinstance(t, str) else "".join(t) for t in test])
        #print(c, test_str, target, test, tcount)

        tkon = StSt(test_str, skon.mod(no_shapes=True), strip=False)
        if skon_tweak is None:
            tkoff = StSt(test_str, skoff, strip=False)
            tkoff_tweak = None
        else:
            tkoff = StSt(test_str, skoff.mod(no_shapes=True), strip=False)
            skoff_tweak = skon_tweak.mod(kern=0, kern_pairs={}, kp={}, tu=0)
            tkoff_tweak = StSt(test_str, skoff_tweak, strip=False)

        if idx == 0:
            if tkoff_tweak:
                tkoff_frame = tkoff[0].data("frame")
                th = skon_tweak.input["kwargs"].get("th", 0)
                tv = skon_tweak.input["kwargs"].get("tv", 0)
                tkoff_glyph = tkoff_tweak[0].align(tkoff_frame, th=th, tv=tv)
                tkoff_glyph.data(frame=tkoff_frame)
            else:
                tkoff_glyph = tkoff[0]#.copy(with_data=True)
            
            dps.append(tkoff_glyph)
            prev = krn(tkoff, tkon, 1)
        if target > 0:
            _prev = krn(tkoff, tkon, 1)
            prev_av = (prev+_prev)/2

            if tkoff_tweak:
                tkoff_frame = tkoff[1].data("frame")
                th = skon_tweak.input["kwargs"].get("th", 0)
                tv = skon_tweak.input["kwargs"].get("tv", 0)
                tkoff_glyph = tkoff_tweak[1].align(tkoff_frame, th=th, tv=tv)
                tkoff_glyph.data(frame=tkoff_frame)
            else:
                tkoff_glyph = tkoff[1].copy(with_data=True)
            
            dps.append(tkoff_glyph.translate(-kx(tkoff, 1), 0))
            tracks.append(-prev_av)

            if tcount > 2:
                #print("_PREV", _prev)
                _next = krn(tkoff, tkon, 2) - _prev #tkoff[0].ambit().w
                #print("next", _next)
            else:
                _next = 0
            prev = _next
    
    #print(tracks)
    return dps.distribute(
        tracks=tracks
    )