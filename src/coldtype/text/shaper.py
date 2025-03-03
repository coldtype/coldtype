import re
import unicodedata
from itertools import groupby

def between(c, a, b):
    return ord(a) <= ord(c) <= ord(b)

LATIN = lambda c: between(c, '\u0000', '\u024F')
KATAKANA = lambda c: between(c, '\u30A0', '\u30FF')
HIRAGANA = lambda c: between(c, '\u3040', '\u309F')
CJK = lambda c: between(c, '\u4E00', '\u9FFF')

modes = [
    "LATIN",
    "ARABIC",
    "HEBREW",
    "SPACE",
    "CJK",
    "HANGUL",
    "KATAKANA",
]

def segment(txt, mode="LATIN", includeNames=False, print_characters=False):
    current_mode = mode
    runs = [[mode]]
    for i, c in enumerate(txt):
        try:
            n = unicodedata.name(c)
        except ValueError:
            n = "PRIVATE"
        
        if print_characters:
            print(">", n)
        
        for m in modes:
            if m in n:
                if current_mode != m:
                    current_mode = m
                    runs.append([m])
        runs[-1].append((n, c) if includeNames else c)
    
    if len(runs[0]) == 0:
        runs = runs[1:]
    
    for idx, (mode, *run) in enumerate(runs):
        p = runs[idx-1] if idx > 0 else None
        n = runs[idx+1] if len(runs) > idx+1 else None
        if p and n:
            if mode == "SPACE" and p[0] == n[0]:
                runs[idx][0] = p[0]
    
    grouped_runs = []
    for k, g in groupby(runs, lambda e: e[0]):
        txt = "".join(["".join(g[1:]) for g in list(g)])
        if txt:
            found_modes = set()
            for c in txt:
                try:
                    n = unicodedata.name(c)
                except ValueError:
                    n = "PRIVATE"
                for m in modes:
                    if m in n:
                        found_modes.add(m)
            grouped_runs.append((found_modes, txt))
    
    # reverse number ranges in arabic
    for idx, (cats, line) in enumerate(grouped_runs):
        if "ARABIC" in cats or "HEBREW" in cats:
            grouped_runs[idx] = (cats, re.sub("[0-9]+", lambda m: m.group()[::-1], line))

    return grouped_runs

if __name__ == "__main__":
    from pprint import pprint
    s = "ABC (جاف + رطب (ما قبل"
    s = "(رطب (ما قبل"
    #s = "Ali الملخبط Boba"
    s = "وصل الإستيرِوﬂLim/Satلل"
    runs = segment(s, "LATIN")
    pprint(runs)