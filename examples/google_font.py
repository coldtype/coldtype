from coldtype import *

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
        .align(f.a.r, th=0, tv=1)
        .f(0))