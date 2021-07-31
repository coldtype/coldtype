
Rect(angles)
============

Quick reference for common rectangles operations:

.. code:: python

    from coldtype import Rect

    # N.B. Coldtype has point (0,0) at bottom-left

    # three equivalent ways to declare a rect
    
    a = Rect(0, 0, 1080, 1080) # x, y, w, h
    b = Rect(1080, 1080) # just 2 args will be w & h
    c = Rect([0, 0, 1080, 1080]) # can also be 1-arg (a list)

    # simple modifications
    
    r = Rect(1080, 1080)
    a = r.inset(100, 100) # 100-px padding on all sides
    b = r.inset(200, 50) # 200-px inset on left side and right side, 50-px inset on the top and bottom
    c = r.offset(10, 20) # 10-px translation on x-axis (i.e. to-the-right), 20-px translation on y-axis (i.e. up)

    # getting values from a rect
    
    r = Rect(1080, 1080)
    r.x # x coordinate of bottom-left
    r.y # y coordinate of bottom-left
    r.w # width
    r.h # height
    # -or-
    r[0] # x
    r[1] # y
    r[2] # w
    r[3] # h
    x, y, w, h = r
    
    # can be splat'd
    def use_rect(x, y, w, h):
        return x + w, y + h
    use_rect(*r)

    # compass points
    
    r.pc # point-center
    r.pn # point-north
    r.ps # point-south
    r.pe, r.pw # point-east, point-west
    r.pne, r.pse, r.psw, r.pnw # northeast, southeast, southwest, northwest
    # all of these values yield a Point object, which has x/y props & behaves like a list
    r.pc.x # x coordinate of the center of the rect
    r.pc.y # y coordinate of the center of the rect
    r.pc[0] # x
    r.pc[1] # y

    # quick columns
    
    r = Rect(0, 0, 1080, 1080)
    a, b, c = r.subdivide(3, "mnx") # 'a' would be the first column, 'c' the last (left-to-right)
    a, b, c, d = r.subdivide(4, "mxx") # 'a' would be the first column, 'd' the last (right-to-right)
    columns = r.subdivide(8, "W") # columns holds a list of 8 columns arrayed west-to-east (left-to-right) (b/c of the W argument, equivalent to "mnx")

    # quick rows
    
    a, b, c, d = r.subdivide(4, "mxy") # 'a' would be the first row, 'd' the last (top-to-bottom)
    a, b, c, d = r.subdivide(4, "mxy") # 'a' would be the first row, 'd' the last (top-to-bottom)
    rows = r.subdivide(8, "N") # rows holds a list of 8 rows arrayed north-to-south (top-to-bottom) (b/c of the "N" argument, equivalent to "mxy")

    # quick slicing and dicing
    
    r = Rect(1080, 1080)
    r.take(100, "W") # 100px-wide rect sliced off the western half of the original rect, i.e. Rect(0, 0, 100, 1080)

    # "edge" shorthand

    "mnx" == "W" == "⊢" # aka minimum-x aka the left-hand edge of a rectangle, aka the western edge
    "mny" == "S" == "⊥" # aka minimum-y aka the bottom edge of a rectangle, aka the southern edge
    "mxx" == "E" == "⊣" # aka maximum-x aka the right-hand edge of a rectangle, aka the eastern edge
    "mxy" == "N" == "⊤" # aka maximum-y aka the top edge of a rectangle, aka the northern edge
    "mdx" == "CX" == "⌶" # aka middle-x aka the center vertical "edge", or line of a rectangle (a line going from the top to the bottom right down the middle)
    "mdy" == "CY" == "Ｈ" # aka middle-y aka the center horizontal "edge" of a rectangle (a line going from the left to the right right through the middle (separating the bottom half from the top half))