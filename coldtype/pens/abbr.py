from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.text.reader import StyledString, Style
from coldtype.pens.dp_auto_abbrev import *
from coldtype.color import *

def end():
    return ["end"]

def skip(*instructions):
    return ["skip"]

def _build(seed_class, seed, instructions):
    if seed:
        dp = seed
    else:
        dp = seed_class()

    def realize_string():
        txt = dp["text"]
        if "style" in dp:
            fnt = dp["font"]
            props = dp["style"]
        elif "font" in dp:
            fnt = dp["font"]
            props = dict(fontSize=250)
        elif "font" not in dp:
            raise Exception("No font provided in abbr-string")
        
        stst = StyledString(txt, Style(fnt, **props))
        if seed_class == DATPen:
            return stst.pen()
        elif seed_class == DATPenSet:
            return stst.pens()
        else:
            raise Exception("WTF")

    for _args in instructions:
        try:
            if _args[0] == "skip":
                continue
        except:
            pass
        
        if not _args:
            continue
        elif isinstance(_args, StyledString): # TODO could be lazy?
            stst = _args
            if seed_class == DATPen:
                dp = stst.pen()
            elif seed_class == DATPenSet:
                dp = stst.pens()
        elif isinstance(_args, DATPen):
            if seed_class == DATPen:
                if len(dp) == 0:
                    dp = _args
                else:
                    dp.record(_args)
            else:
                dp.append(_args)
        elif isinstance(_args, DATPenSet):
            dp.append(_args)
        else:
            fn, *args = _args
            if fn == "text":
                dp = dict(pen=dp, text=args[0])
            elif fn == "font":
                dp = dict(pen=dp.get("pen"), text=dp["text"], font=args[0]) # text, fontName
            elif fn == "style":
                dp = dict(pen=dp.get("pen"), text=dp["text"], font=dp["font"], style=args[0])
            else:
                # realize the string if it's still latent
                if isinstance(dp, dict):
                    pen = dp.get("pen")
                    dp = realize_string()
                    if pen and len(pen) > 0:
                        dp = DATPenSet([pen, dp])
                
                if fn == "end":
                    return dp
                elif fn == "skip":
                    continue
                elif fn == "wrap":
                    seed_class = DATPenSet
                    dp = DATPenSet([dp])
                elif fn == "subinstructions":
                    dp = _build(seed_class, dp, args)
                else:
                    try:
                        dp = getattr(dp, fn)(*args)
                    except Exception as e:
                        print("--------------------")
                        print(fn, args)
                        print(e)
    
    if isinstance(dp, dict):
        pen = dp.get("pen")
        dp = realize_string()
        if pen:
            dp = DATPenSet([pen, dp])
    return dp

def pen(*instructions):
    return _build(DATPen, None, instructions)

def s_pen(*instructions):
    return ["skip"]

def pens(*instructions):
    return _build(DATPenSet, None, instructions)

def s_pens(*instructions):
    return ["skip"]

def wrap():
    return ["wrap"]

def fsw(f=None, s=None, sw=0):
    return [
        "subinstructions",
        fill(f),
        stroke(s) if s else None,
        strokeWidth(sw) if sw > 0 else None,
    ]

def s_fsw(*args, **kwargs):
    return ["skip"]

def text(text):
    return ["text", text]

def s_text(*args, **kwargs):
    return ["skip"]

def font(fnt):
    return ["font", fnt]

def s_font(*args, **kwargs):
    return ["skip"]

def style(fontSize, **properties): # properties here could have some autocomplete?
    return ["style", {**dict(fontSize=fontSize), **properties}]

def s_style(*args, **kwargs):
    return ["skip"]

G = Gradient