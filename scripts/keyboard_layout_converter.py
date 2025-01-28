from coldtype import *
from coldtype.renderer.keyboard import symbol_to_glfw, SHORTCUTS

keyboards = {
    "fr": {
        "q": "a",
        "w": "z",
        "e": "e",
        "r": "r",
        "t": "t",
        "y": "y",
        "u": "u",
        "i": "i",
        "o": "o",
        "p": "p",
        "[": "^",
        "{": "¨",
        "]": "$",
        "}": "£",
        "|": "µ",
        "`": "²",
        "~": "~",
        "a": "q",
        "s": "s",
        "d": "d",
        "f": "f",
        "g": "g",
        "h": "h",
        "j": "j",
        "k": "k",
        "l": "l",
        ";": "m",
        ":": "M",
        "'": "ù",
        "\"": "%",
        "z": "w",
        "x": "x",
        "c": "c",
        "v": "v",
        "b": "b",
        "n": "n",
        "m": ",",
        ",": ";",
        "<": ".",
        ".": ":",
        ">": "/",
        "/": "!",
        "?": "§",
        "@": "2",
        "#": "3",
        "$": "4",
        "^": "6",
        "&": "7"
    }
}

ALT_LOOKUP = {
    "[": "<bracket-right>",
    "]": "<bracket-left>",
    "\\": "<backslash>",
}

REV_ALT_LOOKUP = {v:k for k,v in ALT_LOOKUP.items()}

valid_keys = set()

for k, v in SHORTCUTS.items():
    for n in v:
        if n[1] in REV_ALT_LOOKUP:
            valid_keys.add(REV_ALT_LOOKUP[n[1]])
        else:
            valid_keys.add(n[1])

remaps = {}

for name, keyboard in keyboards.items():
    remaps[name] = {}
    for k, v in keyboard.items():
        if k != v:
            if k in valid_keys:
                if k in ALT_LOOKUP: k = ALT_LOOKUP[k]
                if v in ALT_LOOKUP: v = ALT_LOOKUP[v]
                try:
                    remaps[name][symbol_to_glfw(k)] = symbol_to_glfw(v)
                except:
                    print("UNMAPPABLE", k, v)

print(remaps)

@animation((100, 100))
def scratch(f:Frame):
    return None