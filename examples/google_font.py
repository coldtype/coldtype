from coldtype import *

# if you're running this on windows, you'll
# probably need to do an `export PYTHONUTF8=1`
# in your shell before running it, or else
# python won't be able to understand these strings

pairs = [
    ["Noto Sans Tamil", "ஐக்கிய நாடுகள்"],
    ["Noto Sans Balinese", "ᬏᬢᬤᬢᬶᬭᬶᬓ᭄ᬢᬫ᭄,"],
    ["Noto Sans Telugu", "ఈ స్వత్వములను"],
    ["Noto Sans Bengali", "গাসৈ সুবুঙানৗ উদাংয়ৈ"],
    ["Noto Sans Sundanese", "ᮞᮊᮥᮙ᮪ᮔ ᮏᮜ᮪ᮙ ᮌᮥᮘᮢᮌ᮪"]
]

@animation((1080, 540), tl=len(pairs), bg=1)
def nabla1(f):
    font_name, text = pairs[f.i]
    return (StSt(text, Font.GoogleFont(font_name)
        , fontSize=50)
        .align(f.a.r, tx=0, ty=1)
        .f(0))