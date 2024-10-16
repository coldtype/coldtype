from coldtype import *

fonts = Font.LibraryList(r".*")

symbol = "♔"
found = False

print(Font.LibraryFind("Arial Unicode.ttf"))

@animation((540, 540), tl=Timeline(len(fonts), 60), bg=0)
def finder(f):
    global found
    found = False

    print(fonts[f.i])
    font = Font.LibraryFind(fonts[f.i])
    print(font)

    try:
        res = (StSt(symbol, font, 500)
            .align(f.a.r)
            .f(1))
        if res[0].glyphName not in [".notdef", "uni0019", "uni0001", "glyph0", "uni0000"]:
            found = True
            print(">>>"*30)
            print(f.i, f.t.duration, font.path.name, res[0].glyphName)
            print("---"*30)
            print(font.path)
            print("---"*30)
            return res.data(sleep=3)
    except:
        pass
    
    return StSt(str(f.i), Font.JBMono(), 20).f(1).align(f.a.r, tx=0)

def didPreview():
    from time import sleep
    if found:
        sleep(2)