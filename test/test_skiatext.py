from coldtype import *

@renderable((1000, 300))
def test_return_string(r):
    dps = DATPenSet([
        (StyledString("COLDTYPE",
            Style("assets/ColdtypeObviously-VF.ttf", 150))
            .pens()
            .align(r.take(80, "mdy").take(0.9, "mdx"), "mnx")
            .translate(2, 17)
            .f(hsl(0.9)))
    ])
    dps += (DATText("COLDTYPE",
        #Style("Times", 100, load_font=False),
        Style("assets/ColdtypeObviously-VF.ttf", 150, fill=(0, 0.5)),
        r.take(80, "mdy").take(0.9, "mdx")))
    
    return dps