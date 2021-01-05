from coldtype.test import *

vinila = Font.Cacheable("~/Type/fonts/fonts/_wdths/Vinila-VF-HVAR-table.ttf")

@test()
def varfont(r):
    dp = (Slug("Boa!",
            Style(vinila, 340, wdth=0, wght=1, slnt=1, ro=0))
            .pens()
            #.removeOverlap()
            )
    dps = (DATPens([dp])
        .pen()
        .removeOverlap()
        )
    
    print(dps)
    return dps.f(None).s(0).sw(2)