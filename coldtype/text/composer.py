#from coldtype.pens.draftingpens import DraftingPen, DraftingPens
from coldtype.pens.draftingpens import DraftingPens
from coldtype.geometry import Rect, Point

from coldtype.text.shaper import segment
from coldtype.text.reader import Style, StyledString, FittableMixin, Font, normalize_font_path, SegmentedString,  _PenClass, _PensClass


class GrafStyle():
    def __init__(self, leading=10, x="centerx", xp=0, width=0, **kwargs):
        self.leading = kwargs.get("l", leading)
        self.x = x
        self.xp = xp
        self.width = width


class Graf():
    def __init__(self, lines, container, style=None, **kwargs):
        if isinstance(container, Rect):
            self.container = _PenClass().rect(container)
        else:
            self.container = container
        if style and isinstance(style, GrafStyle):
            self.style = style
        else:
            self.style = GrafStyle(**kwargs)
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
    
    def pens(self, align=False):
        rects = self.lineRects()
        pens = _PensClass()
        for idx, l in enumerate(self.lines):
            r = rects[idx]
            dps = l.pens().translate(r.x, r.y) # r.x
            dps.addFrame(Rect(r.x, r.y, r.w, r.h))
            #if align:
            #    dps.container = Rect(0, r.y, r.w, r.h)
            #    dps.align(dps.container, x=self.style.x, y=None)
            pens.append(dps)
        return pens
    
    def fpa(self, rect=None):
        return self.fit().pens().align(rect or self.container.ambit())


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
                    pens.extend(dps._pens)
            else:
                dps = s.pen()
                dps.translate(x_off, 0)
                pens.append(dps)
            x_off += dps.ambit().w
            try:
                x_off += s.margin[1]
                x_off += s.strings[-1].tracking
            except:
                pass
        return _PensClass(pens)
    
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
        
        In the return ``DATPens``, each line will be a ``DATPens``, then within those lines, each glyph/ligature for that line will be an individual ``DATPen``
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
    xa="mdx",
    **kwargs):
    
    if isinstance(font, Style):
        style = font
    else:
        style = Style(font, font_size, **kwargs)
    
    fit = kwargs.get("fit", None)
    leading = kwargs.get("leading", 10)

    if "\n" in text:
        lockup = Composer(rect, text, style, fit=fit, leading=leading).pens()
        if xa:
            lockup = lockup.xa(xa)
    else:
        lockup = StyledString(text, style)
        if fit:
            lockup.fit(fit)
        lockup = lockup.pens()
    return lockup

def Glyphwise(st, styler):
    def kx(dps, idx):
        return dps[idx].ambit().x
    
    def krn(off, on, idx):
        return kx(off, idx) - kx(on, idx)

    dps = DraftingPens()
    prev = 0
    tracks = []

    for idx, c in enumerate(st):
        test = c
        target = 0
        if idx < len(st) - 1:
            test = test + st[idx+1]
        if idx > 0:
            test = st[idx-1] + test
            target = 1
        
        skon = styler(idx, c)
        skoff = skon.mod(kern=0)

        tkon = StSt(test, skon)
        tkoff = StSt(test, skoff)

        if idx == 0:
            dps.append(tkoff[0])
            prev = krn(tkoff, tkon, 1)
        if target > 0:
            _prev = krn(tkoff, tkon, 1)
            prev_av = (prev+_prev)/2
            #print(prev_av, kx(tkoff, 1))

            dps.append(tkoff[1].copy(with_data=True)
                .translate(-kx(tkoff, 1), 0))
            tracks.append(-prev_av)

            if len(test) > 2:
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