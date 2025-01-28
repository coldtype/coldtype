from coldtype import *
from coldtype.renderer.keyboard import symbol_to_glfw, SHORTCUTS

import json

# layouts downloaded from https://github.com/ai/convert-layout

layouts = [x for x in list(Path("~/Downloads/convert-layout-main").expanduser().glob("*.json")) if x.stem not in ["package"]]

keyboards = {l.stem:json.loads(l.read_text()) for l in layouts}

for layout in layouts:
    print(layout)

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

remaps = {k:v for k,v in remaps.items() if len(v) > 0}

#print(list(remaps.keys()))

import black
print(black.format_str(str(remaps), mode=black.Mode(line_length=300)))

#for k, remap in remaps.items():
#    print(k, remap)

@animation((100, 100))
def scratch(f:Frame):
    return None