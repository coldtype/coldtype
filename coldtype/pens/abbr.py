from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.text.reader import StyledString, Style
from coldtype.pens.dp_auto_abbrev import *
from coldtype.color import *

def end():
    return ["end"]

def skip(*instructions):
    return ["skip"]

def _build(seed, instructions):
    dp = seed

    def realize_string(txt, fnt, props):
        stst = StyledString(txt, Style(fnt, **props))
        if isinstance(seed, DATPen):
            return stst.pen()
        elif isinstance(seed, DATPenSet):
            return stst.pens()
        else:
            raise Exception("WTF")

    for _args in instructions:
        if isinstance(_args, StyledString): # TODO could be lazy?
            stst = _args
            if isinstance(seed, DATPen):
                dp = stst.pen()
            elif isinstance(seed, DATPenSet):
                dp = stst.pens()
        else:
            fn, *args = _args
            if fn == "text":
                dp = dict(text=args[0])
            elif fn == "font":
                dp = dict(text=dp["text"], font=args[0]) # text, fontName
            elif fn == "style":
                dp = dict(text=dp["text"], font=dp["font"], style=args[0])
            else:
                # realize the string if it's still latent
                if isinstance(dp, dict):
                    if "style" in dp:
                        dp = realize_string(
                            dp["text"],
                            dp["font"],
                            dp["style"])
                    elif "font" in dp:
                        dp = realize_string(
                            dp["text"],
                            dp["font"],
                            dict(fontSize=250))
                    elif "font" not in dp:
                        raise Exception("No font provided in abbr-string")
                
                if fn == "end":
                    return dp
                elif fn == "skip":
                    continue
                elif fn == "subinstructions":
                    dp = _build(dp, args)
                else:
                    dp = getattr(dp, fn)(*args)
    return dp

def pen(*instructions):
    return _build(DATPen(), instructions)

def pens(*instructions):
    return _build(DATPenSet(), instructions)

def fsw(f=None, s=None, sw=0):
    return [
        "subinstructions",
        fill(f),
        stroke(s),
        strokeWidth(sw),
    ]

def ß(text):
    return ["text", text]

def ƒ(font):
    return ["font", font]

def ƒƒ(fontSize, **properties): # properties here could have some autocomplete?
    return ["style", {**dict(fontSize=fontSize), **properties}]

text = ß
font = ƒ
style = ƒƒ