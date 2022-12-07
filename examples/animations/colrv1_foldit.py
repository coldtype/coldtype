from coldtype import *

at = AsciiTimeline(2, 30, """
[fold       ]              <
              [it        ]
""")

@animation((1080, 540/2), timeline=at, bg=0)
def test1(f):
    font = Font.Find("Foldit\[wght\]")
    text = "Foldit"

    br = (Glyphwise(text, lambda g: Style(font
            , fontSize=200
            , wght=at.ki("it").io(10, ["eei", "eeo"]) if g.i > 3
                else at.ki("fold").io(10)))
            .align(f.a.r, tx=0, ty=0))
    
    return P(
        br,
        #br.substructure()
        )

release = test1.export("h264", loops=3)