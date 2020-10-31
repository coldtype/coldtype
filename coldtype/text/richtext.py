from coldtype.pens.datpen import DATPenSet
from coldtype.text.composer import Graf, GrafStyle, Lockup
from coldtype.text.reader import StyledString


"""
Very experimental module to support rich-text from annotated strings, like a super-minimal-but-open-ended subset of markdown, inspired by the way rich text is built up in the animation.nle.premiere DPS subclass
"""


class RichText(DATPenSet):
    def __init__(self, text, render_text_fn, rect, fit=None, graf_style=GrafStyle(leading=20),):
        super().__init__()
        self.pens = self.parse_block(text, render_text_fn, rect, fit, graf_style).pens

    def parse_block(self, txt, render_text_fn, rect, fit, graf_style):
        parsed_lines = []

        for line in txt.strip().splitlines():
            line_meta = []
            line_result = []
            for slug in reversed(line.strip().split(" ")):
                if slug.startswith("["): # line meta
                    line_meta = slug.strip("[]").split(",")
                else:
                    ps = slug.split("[")
                    meta = []
                    if len(ps) > 1:
                        ps2 = ps[1].split("]")
                        meta = ps2[0]
                    all_meta = [*meta, *line_meta]
                    line_result.insert(0, [ps[0]+" ", all_meta])
            line_result[-1][0] = line_result[-1][0][:-1]
            parsed_lines.append(line_result)

        lines = []
        groupings = []

        for idx, line in enumerate(parsed_lines):
            slugs = []
            texts = []
            for txt, styles in line:
                ftxt, style = render_text_fn(txt, styles)
                texts.append([ftxt, idx, style])

            grouped_texts = []
            idx = 0
            done = False
            while not done:
                style = texts[idx][2]
                grouped_text = [texts[idx]]
                style_same = True
                while style_same:
                    idx += 1
                    try:
                        next_style = texts[idx][2]
                        if next_style == style:
                            style_same = True
                            grouped_text.append(texts[idx])
                        else:
                            style_same = False
                            grouped_texts.append(grouped_text)
                    except IndexError:
                        done = True
                        style_same = False
                        grouped_texts.append(grouped_text)

            for gt in grouped_texts:
                full_text = "".join([t[0] for t in gt])
                slugs.append(StyledString(full_text, gt[0][2]))
            groupings.append(grouped_texts)
            lines.append(slugs)

        lockups = []
        for line in lines:
            lockup = Lockup(line, preserveLetters=True, nestSlugs=True)
            if fit:
                lockup.fit(fit)
            lockups.append(lockup)
        graf = Graf(lockups, rect, graf_style)
        pens = graf.pens()#.align(rect, x="minx")
        group_pens = DATPenSet()

        pens.reversePens()
        for line in pens:
            line.reversePens()
            for slug in line:
                slug.reversePens()
        return pens