from coldtype import *

txt = """
1   Print
2   Photograph
3   Crumple
4   goto 2
"""

@renderable("letter-landscape", bg=1, render_bg=0, fmt="pdf")
def printed(r):
    return (StSt(txt, "polymath", 72, space=300, tu=0, opsz=1, case="lower", leading=34, tnum=1, wght=0.65)
        .align(r)
        .f(0))

def release(_):
    import cups

    path = printed.render_to_disk()[0]
    conn = cups.Connection()
    printers = conn.getPrinters()
    print(printers)

    conn.printFile(conn.getDefault(), str(path), printed.name, {"orientation-requested": "4"})
    import cups