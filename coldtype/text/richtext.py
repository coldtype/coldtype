import re

from coldtype.pens.datpen import DATPenSet
from coldtype.text.composer import Graf, GrafStyle, Lockup
from coldtype.text.reader import StyledString, Style

from pathlib import PurePath
from typing import Optional, List, Callable, Tuple

try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatter import Formatter
    from pygments.token import Token
except ImportError:
    highlight = None
    pass

"""
Very experimental module to support rich-text from annotated strings, like a super-minimal-but-open-ended subset of markdown, inspired by the way rich text is built up in the animation.nle.premiere DPS subclass
"""


class RichText(DATPenSet):
    def __init__(self,
        text,
        render_text_fn:Callable[[str, List[str]], Tuple[str, Style]],
        rect,
        fit=None,
        graf_style=GrafStyle(leading=20),
        tag_delimiters=["[", "]"],
        visible_boundaries=[" "],
        invisible_boundaries=[]):
        "WIP"
        super().__init__()
        self.tag_delimiters = tag_delimiters
        self.visible_boundary_chars = visible_boundaries
        self.invisible_boundary_chars = invisible_boundaries
        
        if isinstance(text, PurePath):
            text = text.read_text()
        
        self.pens = self.parse_block(text, render_text_fn, rect, fit, graf_style).pens

    def parse_block(self, txt, render_text_fn, rect, fit, graf_style):
        parsed_lines = []
        alt_parsed_lines = []

        for line in txt.splitlines():
            line_meta = []
            line_result = []

            i = 0
            in_tag = False
            bnd_char = ""
            si = 0
            slugs = {0:""}
            metas = {0:""}
            bnds = {0:""}

            while i < len(line):
                if in_tag:
                    if line[i] == self.tag_delimiters[1]:
                        in_tag = False
                    else:
                        metas[si] += line[i]
                elif line[i] == self.tag_delimiters[0]:
                    in_tag = True
                
                elif line[i] in self.visible_boundary_chars or line[i] in self.invisible_boundary_chars:
                    bnd_char = line[i]
                    bnds[si] = bnd_char
                    si += 1
                    slugs[si] = ""
                    metas[si] = ""
                    bnds[si] = ""
                else:
                    slugs[si] += line[i]
                i += 1
            
            if not list(slugs.values())[-1]:
                line_meta = list(metas.values())[-1]
                bnds[si-1] = ""
            else:
                line_meta = []
            
            alt_line_result = []
            for i, slug in slugs.items():
                b = bnds[i]
                if b in self.invisible_boundary_chars:
                    b = ""
                alt_line_result.append([
                    slug + b,
                    [*[metas[i]], *line_meta]
                ])
            alt_parsed_lines.append(alt_line_result)

        parsed_lines = alt_parsed_lines
        #from pprint import pprint
        #pprint(parsed_lines)

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


if highlight:

    class ColdtypeFormatter(Formatter):
        def format(self, tokensource, outfile):
            for ttype, token in tokensource:
                if ttype != Token.Text:
                    tt = re.sub(r"^Token\.", "", str(ttype))
                    outfile.write(f"¬{token}≤{tt}≥")
                else:
                    outfile.write(token)
    

    class HTMLRichText(RichText):
        def __init__(self,
            text,
            render_text_fn:Callable[[str, List[str]], Tuple[str, Style]],
            rect,
            fit=None,
            graf_style=GrafStyle(leading=20)):

            if isinstance(text, PurePath):
                text = text.read_text()

            txt = highlight(text, PythonLexer(), ColdtypeFormatter())
            super().__init__(
                txt, render_text_fn, rect,
                fit=fit, graf_style=graf_style,
                tag_delimiters=["≤", "≥"],
                visible_boundaries=[],
                invisible_boundaries=["¬"])