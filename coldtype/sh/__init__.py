import re
from pprint import pprint
from more_itertools import split_at, split_before
from drafting.geometry import Point, Line, Rect
from drafting.sh.context import SHLookup, SHContext


SH_UNARY_SUFFIX_FUNCS = {
    "~": "reverse",
    "¶": "to_pen",
}

SH_UNARY_TO_STRING = {
    "⊢": "w",
    "⊣": "e",
    "⊤": "n",
    "⊥": "s",
    "⌶": "cx",
    "Ｈ": "cy",
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

SH_UNARY_SUFFIX_PROPS = {
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
    "⍵": "end",
    "µ": "mid",
}

SH_BINARY_OPS = {
    "I": "inset",
    "O": "offset",
    "C": "columns",
    "R": "rows",
    "@": "__getitem__",
    "↕": "extr",
    #"P": "project",
    "∏": "project",
    "π": "pinch",
    "†": "take_curve",
}

SH_BINARY_OPS_EDGEAWARE = {
    "T": "take",
    "S": "subtract",
    "E": "expand",
    "M": "maxima",
}

SH_JOINS = {
    "⨝": ["join"],
    "∩": ["intersection"],
    "∮": lambda a, b: f"DraftingPen().moveTo({a}.start).lineTo({a}.end).lineTo({b}.end).lineTo({b}.start).closePath()",
    "⫎": lambda a, b: f"Rect.FromPoints({a}, {b})"
}

SH_BACKREFS = {
    "〱": "_last",
}

SH_EXPLODES = {
    "〻": "_last",
}

SH_PATH_OPS = {
    "ɜ": "endPath",
    "ɞ": "closePath",
    "Я": "reverse"
}

def shchain(s):
    chars = list(SH_BINARY_OPS_EDGEAWARE.keys())
    chars.extend(SH_BINARY_OPS.keys())
    chars.extend(SH_UNARY_SUFFIX_PROPS)
    chars.extend(SH_UNARY_SUFFIX_FUNCS)
    chars.append(">")
    chars.append("Ƨ")
    
    cs = ["".join(x) for x in split_before(s, lambda x: x in chars) if x[0] != ">"]
    out = cs[0]
    spre = re.compile(",|—")
    skip = False

    for c in cs[1:]:
        f = c[0]
        if f == "Ƨ":
            skip = True
            continue
        elif skip:
            skip = False
            continue

        if f in SH_BINARY_OPS:
            fn = SH_BINARY_OPS[f]
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
        elif f in SH_BINARY_OPS_EDGEAWARE:
            fn = SH_BINARY_OPS_EDGEAWARE[f]
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
                else:
                    raise Exception("Edge not matched", args[0])
                if d == "XY":
                    args[i] = (a[1:], '"'+e+"xy"[i]+'"')
                else:
                    args[i] = (a[1:], '"'+e+d.lower()+'"')
                out += f".{fn}({','.join(args[i])})"
        elif f in SH_UNARY_SUFFIX_PROPS:
            fn = SH_UNARY_SUFFIX_PROPS[f]
            out += f".{fn}" #+ c[1:]
        elif f in SH_UNARY_SUFFIX_FUNCS:
            fn = SH_UNARY_SUFFIX_FUNCS[f]
            out += f".{fn}()" #+ c[1:]
    
    return out

def shterm(s:str):
    return shchain(s)

def shphrase(s):
    terms = []
    splits = list(SH_JOINS.keys())
    for idx, _t in enumerate(split_at(s, lambda x: x in splits, keep_separator=1)):
        t = "".join(_t)
        if idx % 2 == 0:
            terms.append("("+shterm(t)+")")
        else:
            terms.append(t)

    out = ""
    t1 = terms[0]
    i = 1
    if i == len(terms):
        return t1    
    else:
        while i < len(terms):
            op_s = terms[i]
            if op_s in SH_JOINS:
                op = SH_JOINS[op_s]
                t2 = terms[i+1]
                
                for k, v in SH_BACKREFS.items():
                    t2 = t2.replace(k, f"({t1})")
                
                if callable(op):
                    out += op(t1, t2)
                else:
                    out += f"({t1}.{op[0]}({t2}))"
                i += 2
    return out

def shgroup(s):
    if s.startswith("Ƨ"):
        return None

    s = s.replace("(", "[").replace(")", "]")
    rg = re.compile(r"\[([^\]]+)\]")

    def expand(m):
        return f"({shphrase(m.group(1))})"

    rm = rg.findall(s)
    while len(rm) > 0:
        s = rg.sub(expand, s)
        rm = rg.findall(s)
    
    return shphrase(s)

def sh(s, ctx:SHContext=None, dps=None, subs={}):
    from drafting.pens.draftingpen import DraftingPen

    #print("SH>", s, subs)

    if ctx is None:
        ctx = SHContext()

    evaled = []
    last_locals = {**ctx.locals}
    s = s.replace("_", "")
    s = "ƒ"+re.sub(r"[\s\n]+", "ƒ", s).strip()

    def expand_multisuffix(m):
        out = []
        arrows = list(m.group(2))
        for a in arrows:
            out.append(m.group(1)+a)
        return "ƒ".join(out)
    
    def do_eval(phrase):
        py = (shgroup(phrase))
        if not py:
            return None

        for k, v in SH_PATH_OPS.items():
            py = py.replace(k, '"' + v + '"')
        
        for k, v in ctx.lookups.items():
            py = py.replace(v.symbol, f"ctx.{k}.")

        for k, v in ctx.subs.items():
            py = py.replace(k, v(ctx) if callable(v) else v)
        
        for k, v in subs.items():
            py = py.replace(k, str(v))

        #print("EVAL<", py)

        try:
            res = eval(py, dict(
                ctx=ctx,
                _last=evaled[-1] if len(evaled) > 0 else None,
                _dps=dps,
                Point=Point,
                Line=Line,
                Rect=Rect,
                DraftingPen=DraftingPen)
                , last_locals)
            #print("LOCALS", last_locals)
            return res
        except SyntaxError as e:
            print("SYNTAX ERROR", e, phrase, py)
            return None

    #s = re.sub(r"([\$\&]{1}[a-z]+)([↖↑↗→↘↓↙←•⍺⍵µ]{2,})", expand_multisuffix, s)

    # for k, v in SH_PATH_OPS.items():
    #     s = s.replace(k, '"' + v + '"')

    join_to_path = False
    splits = ["ƒ"]
    splits.extend(SH_EXPLODES.keys())

    s = re.sub("ƒ\-[^ƒ]+", "", s)

    for phrase in split_before(s, lambda x: x in splits):
        phrase = "".join(phrase).strip()
        #print("PHRASE", phrase)
        last = None
        if not phrase:
            continue
        if phrase[0] in SH_EXPLODES:
            phrase = "_last"+phrase[1:]
        #    last = evaled[-1]
        if phrase[0] == "ƒ":
            phrase = phrase[1:]
        if not phrase:
            continue

        if phrase == "∫":
            phrase = "'∫'"

        more = []
        if "ø" in phrase:
            phrase = phrase.replace("ø", "")
        elif "|" in phrase:
            tuple = phrase.split("|")
            for i, t in enumerate(tuple):
                if isinstance(t, str):
                    if "∑" in t:
                        t = ",".join([f"'{c}'" for c in t])
                    elif len(t) > 1:
                        if t[0] in SH_UNARY_TO_STRING:
                            tuple[i] = [SH_UNARY_TO_STRING[x] for x in t]
                            continue
                    else:
                        if t in SH_UNARY_TO_STRING:
                            tuple[i] = SH_UNARY_TO_STRING[t]
                            continue
                tuple[i] = do_eval(t)
            more = tuple
            phrase = tuple[-1]

        if more:
            evaled.append(more)
        else:
            evaled.append(do_eval(phrase))
        if dps is not None:
            dps.append(evaled[-1])
    
    ctx.locals = {**ctx.locals, **last_locals}
    return evaled