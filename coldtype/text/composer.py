from coldtype.pens.datpen import DATPen, DATPens
from drafting.geometry import Rect, Point

from coldtype.text.shaper import segment
from coldtype.text.reader import Style, StyledString, FittableMixin, Font, normalize_font_path, SegmentedString


class GrafStyle():
    def __init__(self, leading=10, x="centerx", xp=0, width=0, **kwargs):
        self.leading = kwargs.get("l", leading)
        self.x = x
        self.xp = xp
        self.width = width


class Graf():
    def __init__(self, lines, container, style=None, **kwargs):
        if isinstance(container, Rect):
            self.container = DATPen().rect(container)
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
        box = self.container.getFrame()
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
        pens = DATPens()
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
        return self.fit().pens().align(rect or self.container.getFrame())


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
                    pens.extend(dps.pens)
            else:
                dps = s.pen()
                dps.translate(x_off, 0)
                pens.append(dps)
            x_off += dps.getFrame().w
            try:
                x_off += s.margin[1]
                x_off += s.strings[-1].tracking
            except:
                pass
        return DATPens(pens)
    
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
    
    def pens(self) -> DATPens:
        """
        Structured representation of the multi-line text
        
        In the return ``DATPens``, each line will be a ``DATPens``, then within those lines, each glyph/ligature for that line will be an individual ``DATPen``
        """
        return self.graf.pens()
    
    def pen(self) -> DATPen:
        """
        Entire multiline text as a single vector
        """
        return self.graf.pens().pen()