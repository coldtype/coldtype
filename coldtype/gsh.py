import re
from more_itertools import split_at, split_before
from pprint import pprint

from coldtype import DATPens

GSH_UNARY_SUFFIX_FUNCS = {
    "~": "reverse",
}

GSH_UNARY_TO_STRING = {
    "←": "W",
    "↑": "N",
    "→": "E",
    "↓": "S",
    "↖": "NW",
    "↗": "NE",
    "↘": "SE",
    "↙": "SW",
    "•": "C",
}

GSH_UNARY_SUFFIX_PROPS = {
    "⊢": "ew",
    "⊣": "ee",
    "⊤": "en",
    "⊥": "es",
    "⌶": "ecx",
    "Ｈ": "ecy",
    "←": "pw",
    "↑": "pn",
    "→": "pe",
    "↓": "ps",
    "↖": "pnw",
    "↗": "pne",
    "↘": "pse",
    "↙": "psw",
    "•": "pc",
    "⍺": "start",
    "⍵": "end"
}

GSH_BINARY_OPS = {
    "I": "inset",
    "𝓘": "inset",
    "O": "offset",
    "𝓞": "offset",
    "C": "columns",
    "𝓒": "columns",
    "R": "rows",
    "𝓡": "rows",
    "@": "__getitem__",
    "↕": "extrapolate",
}

GSH_BINARY_OPS_EDGEAWARE = {
    "T": "take",
    "𝓣": "take",
    "S": "subtract",
    "𝓢": "subtract",
    "E": "expand",
    "𝓔": "expand",
    "M": "maxima",
    "𝓜": "maxima"
}

GSH_JOINS = {
    "⨝": ["join"],
    "∩": ["intersection"],
}

GSH_EXPLODES = {
    "〻": ["duplicate"],
}

GSH_PATH_OPS = {
    "ɜ": "endPath", # 'open'
    "ɞ": "closePath", # 'closed'
    "Я": "reverse"
}

def gshchain(s):
    chars = list(GSH_BINARY_OPS_EDGEAWARE.keys())
    chars.extend(GSH_BINARY_OPS.keys())
    chars.extend(GSH_UNARY_SUFFIX_PROPS)
    chars.extend(GSH_UNARY_SUFFIX_FUNCS)
    chars.append(">")
    cs = ["".join(x) for x in split_before(s, lambda x: x in chars) if x[0] != ">"]
    #print(cs)
    
    #cs = s.split(">")
    out = cs[0]
    spre = re.compile(",|—")
    for c in cs[1:]:
        f = c[0]
        if f in GSH_BINARY_OPS:
            fn = GSH_BINARY_OPS[f]
            d = None
            if c[1] in ["X", "Y"]:
                d = c[1]
                args = spre.split(c[2:])
            else:
                args = spre.split(c[1:])
            if d:
                fn += "_" + d.lower()
            for i, a in enumerate(args):
                if a == "auto" or a == "a":
                    args[i] = '"auto"'
            out += f".{fn}({','.join(args)})"
        elif f in GSH_BINARY_OPS_EDGEAWARE:
            fn = GSH_BINARY_OPS_EDGEAWARE[f]
            d = "XY"
            if c[1] in ["X", "Y"]:
                d = c[1]
                args = spre.split(c[2:])
            else:
                args = spre.split(c[1:])
            for i, a in enumerate(args):
                if a[0] == "-":
                    e = "mn"
                elif a[0] == "=":
                    e = "md"
                elif a[0] == "+":
                    e = "mx"
                if d == "XY":
                    args[i] = (a[1:], '"'+e+"xy"[i]+'"')
                else:
                    args[i] = (a[1:], '"'+e+d.lower()+'"')
                out += f".{fn}({','.join(args[i])})"
        elif f in GSH_UNARY_SUFFIX_PROPS:
            fn = GSH_UNARY_SUFFIX_PROPS[f]
            out += f".{fn}"
        elif f in GSH_UNARY_SUFFIX_FUNCS:
            fn = GSH_UNARY_SUFFIX_FUNCS[f]
            out += f".{fn}()"
    return out

def gshterm(s:str):
    return gshchain(s)

def gshphrase(s):
    terms = []
    splits = list(GSH_JOINS.keys())
    for idx, _t in enumerate(split_at(s, lambda x: x in splits, keep_separator=1)):
        t = "".join(_t)
        if idx % 2 == 0:
            terms.append("("+gshterm(t)+")")
        else:
            terms.append(t)
    
    #pprint(terms)

    out = ""
    t1 = terms[0]
    i = 1
    if i == len(terms):
        return t1    
    else:
        while i < len(terms):
            op_s = terms[i]
            if op_s in GSH_JOINS:
                op = GSH_JOINS[op_s]
                t2 = terms[i+1]
                out += f"({t1}.{op[0]}({t2}))"
                i += 2

    return out

def gsh(s, ctx={}):
    dps = DATPens()
    evaled = []
    s = "ƒ"+re.sub(r"[\s\n]+", "ƒ", s).strip()

    def expand_multiarrow(m):
        out = []
        arrows = list(m.group(2))
        for a in arrows:
            out.append(m.group(1)+a)
        return "ƒ".join(out)
    
    def do_eval(phrase, last):
        py = (gshphrase(phrase))
        py = py.replace("$", "ctx.c.")
        py = py.replace("&", "ctx.")
        py = py.replace("■", "ctx.bounds()")
        py = py.replace("□", "_dps.bounds()")
        print("=============", py)
        return eval(py, dict(ctx=ctx, _last=last, _dps=dps))

    s = re.sub(r"([\$\&]{1}[a-z]+)([↖↑↗→↘↓↙←•]{2,})", expand_multiarrow, s)
    #print("---------------------", s)

    for k, v in GSH_PATH_OPS.items():
        s = s.replace(k, '"' + v + '"')

    splits = ["ƒ"]
    splits.extend(GSH_EXPLODES.keys())
    for phrase in split_before(s, lambda x: x in splits):
        phrase = "".join(phrase).strip()
        last = None
        if not phrase:
            continue
        if phrase.startswith("-"):
            continue
        if phrase[0] in GSH_EXPLODES:
            phrase = "_last"+phrase[1:]
            last = evaled[-1]
        elif phrase[0] == "ƒ":
            phrase = phrase[1:]
        if not phrase:
            continue

        more = []
        if "|" in phrase:
            tuple = phrase.split("|")
            for i, t in enumerate(tuple[:-1]):
                if t in GSH_UNARY_TO_STRING:
                    tuple[i] = GSH_UNARY_TO_STRING[t]
                else:
                    tuple[i] = do_eval(t, last)
            #print(tuple[:-1])
            more = tuple[:-1]
            phrase = tuple[-1]
        try:
            ev = do_eval(phrase, last)
            if more:
                evaled.append((*more, ev))
            else:
                evaled.append(ev)
            dps.append(evaled[-1])
        except SyntaxError as e:
            evaled.append(None)
            print("SYNTAX ERROR", e)
    return evaled, dps

# TODO #-support for last... could be one symbol for each of rect,point,line?

if __name__ == "<run_path>":
    from coldtype import *

    #@renderable()
    def test(r):
        dps = DPS().constants(ri=r.inset(50), cf=65)
        e, dps2 = gsh("""
            $ri $ri𝓘100⌶∩$ri𝓘200⊤
            $ri𝓣Y=0.5𝓘X150𝓒20—a—10@1⊥⍺
            $ri𝓘150↖⨝$ri↘〻𝓞X-100 □𝓘100
            """, ctx=dps)
        return [
            dps2.f(None).s(0).sw(5)
        ]
    
    @renderable()
    def test2(r):
        dps = DPS().constants(r=r.inset(50), cf=65)
        e, dps2 = gsh("$r←↓↑ $r↓|45|$r→ ↙|65|$r↑ ɜ Я",
            ctx=dps)
        pprint(e)
        dp = DP()
        dp.mt(e[0])
        for _e in e[1:]:
            if isinstance(_e, Point):
                dp.lt(_e)
            elif isinstance(_e, str):
                getattr(dp, _e)()
            elif len(_e) == 3:
                dp.boxCurveTo(_e[-1], _e[0], _e[1])
        if dp.value[-1][0] not in ["endPath", "closePath"]:
            dp.closePath()
        return dp.f(None).s(0).sw(5)