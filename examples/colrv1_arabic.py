from coldtype import *

text1 = """
از آنجا که عدم شناسائی و تحقیر حقوق
بشر منتهی به اعمال وحشیانه‌ای
"""

@renderable((1080, 340), bg=1)
def arefRuqaa(r):
    return (StSt(text1, "ArefRuqaaInk-Bold", 80, strip=True)
        .xalign(r)
        .lead(60)
        .align(r))

@renderable((1080, 340), bg=1)
def reemKufi(r):
    return (StSt(text1, "ReemKufiInk-Regular", 70, strip=True)
        .xalign(r)
        .lead(60)
        .align(r))

