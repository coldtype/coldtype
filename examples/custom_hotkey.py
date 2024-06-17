from coldtype import *

@renderable((100, 100), bg=hsl(0.9))
def scratch(r):
    return None

def custom_hotkey(key, renderer):
    print(">>>", key, renderer)