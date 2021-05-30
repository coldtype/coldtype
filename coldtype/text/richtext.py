import re

from coldtype.pens.draftingpen import DraftingPen
from coldtype.pens.draftingpens import DraftingPens
from coldtype.text.composer import Graf, GrafStyle, Lockup
from coldtype.text.reader import StyledString, Style
from coldtype.color import hsl

from pathlib import PurePath
from typing import Optional, List, Callable, Tuple, Union
from functools import reduce

try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatter import Formatter
    from pygments.token import Token
except ImportError:
    highlight = None
    pass

class RichText(DraftingPens):
    """Very experimental module to support rich-text from annotated strings, like a super-minimal-but-open-ended subset of markdown, inspired by the way rich text is built up in the time.nle.premiere DPS subclass in coldtype"""
    def __init__(self,
        rect,
        text,
        render_text_fn:Union[dict, Callable[[str, List[str]], Tuple[str, Style]]],
        fit=None,
        graf_style=GrafStyle(leading=20),
        tag_delimiters=["[", "]"],
        visible_boundaries=[" "],
        invisible_boundaries=[],
        union_styles=True,
        blankfill="¶",
        strip=True,
        strip_lines=False):
        super().__init__()
        self.tag_delimiters = tag_delimiters
        self.visible_boundary_chars = visible_boundaries
        self.invisible_boundary_chars = invisible_boundaries
        self.union_styles = union_styles
        self.blankfill = blankfill
        
        if isinstance(text, PurePath):
            text = text.read_text()
        if strip:
            text = text.strip()
        
        if strip_lines:
            text = "\n".join([l.strip() for l in text.split("\n")])
        
        self._pens = self.parse_block(text, render_text_fn, rect, fit, graf_style)._pens

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
                last_key = list(slugs.keys())[-1]
                del slugs[last_key]
                bnds[si-1] = ""
            else:
                line_meta = []
            
            alt_line_result = []
            for i, slug in slugs.items():
                b = bnds[i]
                if b in self.invisible_boundary_chars:
                    b = ""
                styles = []
                if metas[i]:
                    styles.append(metas[i])
                if line_meta:
                    styles.append(line_meta)
                alt_line_result.append([slug + b, styles])
            alt_parsed_lines.append(alt_line_result)

        parsed_lines = []
        for pl in alt_parsed_lines:
            #print(">", pl)
            if pl:
                parsed_lines.append(pl)
            elif self.blankfill:
                parsed_lines.append([[self.blankfill, ["blank"]]])

        lines = []
        groupings = []

        #from pprint import pprint
        #pprint(parsed_lines)

        for idx, line in enumerate(parsed_lines):
            slugs = []
            texts = []
            for txt, styles in line:
                if callable(render_text_fn):
                    ftxt, style = render_text_fn(txt, styles)
                else:
                    style = styles[0] if len(styles) > 0 else "default"
                    ftxt = txt
                    if style in render_text_fn:
                        style = render_text_fn[style]
                    else:
                        style = render_text_fn["default"]
                texts.append([ftxt, idx, style, styles])

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
                        if next_style == style and self.union_styles:
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
                styles = gt[0][3]
                style = gt[0][2].mod()
                style.data = dict(style_names=styles, txt=full_text)
                slugs.append(StyledString(full_text, style))
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
        group_pens = DraftingPens() # TODO configurable?

        pens.reversePens()
        for line in pens:
            line.reversePens()
            for slug in line:
                slug.reversePens()
        return pens
    
    def filter_style(self, style):
        return self.pfilter(lambda i, p: style in p.data.get("style_names", []))
    
    def filter_text(self, text, flags=re.I):
        return self.pfilter(lambda i, p: re.match(text, p.data.get("txt", ""), flags=flags))
    
    def remove_blanklines(self, blank=None):
        if not blank and self.blankfill:
            blank = self.blankfill
        
        for line in self._pens:
            txt = reduce(lambda acc, p: p.data.get("txt", "") + acc, line, "")
            if txt == blank:
                line._pens = [DraftingPen()]
        
        return self


if highlight:

    class ColdtypeFormatter(Formatter):
        def format(self, tokensource, outfile):
            for ttype, token in tokensource:
                if ttype != Token.Text:
                    tt = re.sub(r"^Token\.", "", str(ttype))
                    outfile.write(f"¬{token}≤{tt}≥")
                else:
                    outfile.write(token)
    

    class PythonCode(RichText):
        def __init__(self,
            rect,
            text,
            render_text_fn:Callable[[str, List[str]], Tuple[str, Style]],
            fit=None,
            graf_style=GrafStyle(leading=20)):

            if isinstance(text, PurePath):
                text = text.read_text()

            txt = highlight(text, PythonLexer(), ColdtypeFormatter())
            super().__init__(
                rect, txt, render_text_fn,
                fit=fit, graf_style=graf_style,
                tag_delimiters=["≤", "≥"],
                visible_boundaries=[],
                invisible_boundaries=["¬"])
        
        def DefaultStyles(r, b, bi):
            """regular, bold, bold-italic"""
            return {
                "Keyword": (bi, hsl(0.9, s=0.6)),
                "Keyword.Namespace": (b, hsl(0.2, s=1)),
                "Name.Namespace": (b, hsl(0.55, s=1)),
                "Name.Builtin": (bi, hsl(0.05, s=1)),
                "Name.Function": (bi, hsl(0.65, s=1, l=0.7)),
                "Name.Decorator": (bi, hsl(0.2, 1)),
                "Name": (b, hsl(0.45, 0.7)),
                "Operator": (b, hsl(0.6, s=1)),
                "Operator.Word": (b, hsl(0.9)),
                "Punctuation": (b, hsl(0.8)),
                "Literal.String.Double": (r, hsl(0.15, s=0.7)),
                "Literal.String.Affix": (bi, hsl(0.85, s=1)),
                "Literal.String.Interpol": (b, hsl(0.05, s=1)),
                "Literal.String.Doc": (r, hsl(0.6, l=0.4)),
                "Literal.Number.Float": (r, hsl(0.9, s=0.7)),
                "Literal.Number.Integer": (r, hsl(0.45)),
                "Comment.Single": (r, (0.3)),
                "default": (r, 0.5),
            }
