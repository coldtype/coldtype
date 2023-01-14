from coldtype import *

text1 = """
از آنجا که عدم شناسائی و تحقیر حقوق
بشر منتهی به اعمال وحشیانه‌ای
"""

@renderable((1080, 340), bg=1)
def arefRuqaa(r):
    return (StSt(text1, Font.GoogleFont("Aref Ruqaa Ink"), 80)
        .xalign(r)
        .lead(60)
        .align(r))

@renderable((1080, 340), bg=1)
def reemKufi(r):
    return (StSt(text1, Font.GoogleFont("Reem Kufi Ink"), 70)
        .xalign(r)
        .lead(60)
        .align(r))

