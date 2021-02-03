from coldtype import *
import re
from more_itertools import split_at, split_before
from pprint import pprint

# rg = re.compile("["+"".join(EPL_SYMBOLS.keys())+"]{2,}")
# s = "$ri↑↗↖"
# mm = re.findall(rg, s)
# if mm:
#     first = mm[0][0]
#     a, b = s.split(first)
#     ss = a + first + " " + a + (" " + a).join(mm[0][1:])
#     print(ss.split(" "))

EPL_UNARY_SUFFIX_FUNCS = {
    "~": "reverse",
}

EPL_UNARY_SUFFIX_PROPS = {
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

EPL_BINARY_OPS = {
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

EPL_BINARY_OPS_EDGEAWARE = {
    "T": "take",
    "𝓣": "take",
    "S": "subtract",
    "𝓢": "subtract",
    "E": "expand",
    "𝓔": "expand",
    "M": "maxima",
    "𝓜": "maxima"
}

EPL_JOINS = {
    "⨝": ["join"],
    "∩": ["intersection"],
}

EPL_EXPLODES = {
    "〻": ["duplicate"],
}

def eplchain(s):
    chars = list(EPL_BINARY_OPS_EDGEAWARE.keys())
    chars.extend(EPL_BINARY_OPS.keys())
    chars.extend(EPL_UNARY_SUFFIX_PROPS)
    chars.extend(EPL_UNARY_SUFFIX_FUNCS)
    chars.append(">")
    cs = ["".join(x) for x in split_before(s, lambda x: x in chars) if x[0] != ">"]
    print(cs)
    
    #cs = s.split(">")
    out = cs[0]
    spre = re.compile(",|—")
    for c in cs[1:]:
        f = c[0]
        if f in EPL_BINARY_OPS:
            fn = EPL_BINARY_OPS[f]
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
        elif f in EPL_BINARY_OPS_EDGEAWARE:
            fn = EPL_BINARY_OPS_EDGEAWARE[f]
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
        elif f in EPL_UNARY_SUFFIX_PROPS:
            fn = EPL_UNARY_SUFFIX_PROPS[f]
            out += f".{fn}"
        elif f in EPL_UNARY_SUFFIX_FUNCS:
            fn = EPL_UNARY_SUFFIX_FUNCS[f]
            out += f".{fn}()"
    return out

def eplterm(s:str):
    #for k, v in EPL_UNARY_SUFFIX_PROPS.items():
    #    s = s.replace(k, "." + v)
    #for k, v in EPL_UNARY_SUFFIX_FUNCS.items():
    #    s = s.replace(k, "." + v + "()")
    return eplchain(s)

def eplphrase(s):
    terms = []
    splits = list(EPL_JOINS.keys())
    for idx, _t in enumerate(split_at(s, lambda x: x in splits, keep_separator=1)):
        t = "".join(_t)
        if idx % 2 == 0:
            terms.append("("+eplterm(t)+")")
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
            if op_s in EPL_JOINS:
                op = EPL_JOINS[op_s]
                t2 = terms[i+1]
                out += f"({t1}.{op[0]}({t2}))"
                i += 2

    return out

def epl(s, ctx={}):
    evaled = []
    for phrase in re.split(r"\s|\n", s.strip()):
        phrase = phrase.strip()
        last = None
        if not phrase:
            continue
        if phrase.startswith("-"):
            continue
        if phrase[0] in EPL_EXPLODES:
            phrase = "_last"+phrase[1:]
            last = evaled[-1]
        py = (eplphrase(phrase))
        py = py.replace("$", "ctx.c.")
        py = py.replace("&", "ctx.")
        print(">>>", py)

        try:
            evaled.append(eval(py, dict(ctx=ctx, _last=last)))
        except SyntaxError as e:
            evaled.append(None)
            print("SYNTAX ERROR", e)
    return evaled

@renderable()
def epl1(r):
    dps = DPS().constants(ri=r.inset(50), cf=65)
    e = epl("""
        $ri
        $ri𝓣Y=0.5𝓘X150𝓒20—a—10@1⊥⍺
        $ri𝓘250↗⨝$ri↘ 〻𝓞-50,+50
        """, ctx=dps)
    print(e)
    return [
        #DP(epl("$ri↗⨝$ri⊤~⍵", ctx=dps)),
        DP(e[0]).f(hsl(0.3, a=0.1)),
        DP(e[1]).f(hsl(0.8)),
        DP(e[2]).s(hsl(0.5)) if len(e) > 2 else None,
        DP(e[3]).s(hsl(0.9)) if len(e) > 3 else None
    ]

    ri = r%"Caƒ300ƒa/@1/Raƒ500ƒa/@1"

    dps.guide(test1ƒtest2="$ri/O+100,+40/⊣〻OX-100")
    #print(dps.guides)
    return DP(dps.guides["test2"]).s(0.5).sw(5).f(None)

    a = dps.ep("$ri↗↘ $ri↙OX-40|$cf|#/O-50,+50/← ↖|$cf|#↗").f(0).pens[0]
    b = DP().mt(ri.pne).lt(ri.pse).bct((ri/-50).pw, "SW", dps.c.cf+1).bct(ri.pne, "NW", dps.c.cf+1).cp().f(0)

    #print(Rect(0, 0) % "Line(Point(10, 10), Point(50, 50))")
    #print(Rect(0, 0) % dps.vs("$ri↗⨝$ri↘"))
    #print(">>>", ri, ri % dps.vs("I10,10"))

    dps2 = DPS().constants(ri=ri).guide(l1=ri.e("⊢"), l2=ri.e("⊤"))
    dps2.ep("$ri↑ $ri⊢∩$ri⊤ $ri/⊥/↕0.1/⍵")

    return DPS([
        DP().gridlines(r, 100, absolute=1),
        DP(ri).f(hsl(0.7, a=0.1)),
        a.copy().xor(b).f(hsl(0.3)),
        a.copy().union(b).f(0, 0.1),
        dps2[0].skeleton().s(0).f(hsl(0.7)),
        #DP(r%"Caƒ100ƒa/@1/⊢/OY100"),
        #DP(r%"I100/SY+100/MX-200/—/OY100"),
        #(DP(r.inset(100).subtract(100, "mxy").setmnx(200).ecy.offset(0, 100)).s(0, 0.2).sw(10)),
    ])