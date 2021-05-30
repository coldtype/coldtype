from coldtype import *
from coldtype.text.composer import Glyphwise

fnt = Font.Cacheable("~/Type/fonts/fonts/OhnoFatfaceVariable.ttf")
#fnt = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

# def Glyphwise(st, styler):
#     def kx(dps, idx):
#         return dps[idx].ambit().x
    
#     def krn(off, on, idx):
#         return kx(off, idx) - kx(on, idx)

#     dps = DPS()
#     prev = 0
#     tracks = []

#     for idx, c in enumerate(st):
#         test = c
#         target = 0
#         if idx < len(st) - 1:
#             test = test + st[idx+1]
#         if idx > 0:
#             test = st[idx-1] + test
#             target = 1
        
#         skon = styler(idx, c)
#         skoff = skon.mod(kern=0)

#         tkon = StSt(test, skon)
#         tkoff = StSt(test, skoff)

#         if idx == 0:
#             dps.append(tkoff[0].f(hsl(random(), a=0.3)))
#             prev = krn(tkoff, tkon, 1)
#         if target > 0:
#             _prev = krn(tkoff, tkon, 1)
#             prev_av = (prev+_prev)/2
#             #print(prev_av, kx(tkoff, 1))

#             dps.append(tkoff[1].copy(with_data=True)
#                 .translate(-kx(tkoff, 1), 0)
#                 .f(hsl(random(), a=0.3)))
#             tracks.append(-prev_av)

#             if len(test) > 2:
#                 #print("_PREV", _prev)
#                 _next = krn(tkoff, tkon, 2) - _prev #tkoff[0].ambit().w
#                 #print("next", _next)
#             else:
#                 _next = 0
#             prev = _next
    
#     #print(tracks)
#     return dps.distribute(
#         tracks=tracks
#     )

@renderable((2400, 1080))
def test_kerned(r):
    st = "AVA"
    fs = 1000
    wdth = 0.43
    kerned = (StSt(st, fnt, fs, kern=1, wdth=wdth, wght=1))
    unkerned = (StSt(st, fnt, fs, kern=0, wdth=wdth, wght=1))
    unkerned2 = (DATPens.Enumerate(st, lambda i,c: StSt(c, fnt, fs, wdth=wdth)))

    gw = Glyphwise(st, lambda i,c: Style(fnt, fs, wdth=wdth, wght=1))
    return DPS([
        kerned.f(hsl(0.9, a=0.5)),
        #kerned.frameSet(),
        #unkerned.f(None).s(0).sw(2).translate(0, 0).removeOverlap(),
        #unkerned2.distribute().translate(0, 20).f(hsl(0.8, a=0.5)),
        gw.f(hsl(0.6, a=0.3)),
        #gw.frameSet(),
    ]).align(r)

@animation((2400, 1080), timeline=60, solo=1, bg=0)
def test_kerned_animation(f):
    return (Glyphwise("WAV", lambda i,c:
        Style(fnt, (fa:=f.adj(-i*10)).e("seio", 1, (250, 500)),
            kern=1, opsz=0, wdth=fa.e("seio", 1)))
        .align(f.a.r, y="mny")
        .f(1))