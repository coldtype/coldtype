Text
====


.. code:: python

    from coldtype import *

    # an exact path to a font file
    fnt = Font.Cacheable("/System/Library/Fonts/SFNS.ttf")

    # listing fonts that match a pattern

    fnt = Font.List("Times") # returns exact paths that can be passed to Font.Cacheable

    # finding and loading the first font matching a pattern

    fnt = Font.Find("Times")

    # The StSt — the quickest way to get from plaintext to a vector/path representation of that text in a given font

    StSt("Text", fnt, 100) # simplest StSt invocation

    # Building and aligning a StSt

    r = Rect(1080, 1080)
    (StSt("Text", fnt, 100)
        .align(r)) # center aligns
    
    (StSt("Text", fnt, 100)
        .align(r, "mnx", "mny")) # align to bottom-left
    
    (StSt("Text", fnt, 100)
        .align(r, "⊢", "⊥")) # also aligns to bottom-left
    
    (StSt("Text", fnt, 100,
        r=1)) # r=1 reverses direction of the glyphs
    
    # Variable fonts

    fnt = Font.Find("SFNS.ttf")

    vtxt = (StSt("Variable", fnt, 100,
        wght=1, opsz=0)) # maximum weight, minimum optical size
    
    vtxt = (StSt("Variable", fnt, 100,
        wght=0, # minimum weight
        opsz=1, # maximum optical size
        ro=1, # remove the overlaps (useful for var fonts when applying a stroke)
        ))
    
    # If your variable font has a width axis, you can pass a fit= argument to a StSt constructor in order to have it automatically fit to a given width — here we'll use the included Mutator Sans fitted to the 

    fit_txt = (StSt("VARIABLE WIDTH", Font.MutatorSans(), 100,
        wdth=1, # fitting always goes from wide to narrow, so make sure to set to max wdth (unless you want it to never be that wide)
        fit=r.w-100) # -100 is just some quick padding
        .align(r))
    
    # Multi-line text
    # N.B. there is no line-breaking in Coldtype; all line-breaks must be manually done (or you can use drawBot as a package within coldtype to generate multi-line strings that can be vectorized with drawBot.BezierPath)

    txt = (StSt("Multi-\nline", fnt, 100, 
        leading=50) # a pixel amount between each line
        .align(r))
    
    txt = (StSt("Multi-\nline", fnt, 100, 
        leading=50, xa="mnx") # left align each line
        .align(r))
    
    txt = (StSt("Multi-\nline", fnt, 100, 
        leading=50, xa="mxx") # right align each line
        .align(r))

    # By default, a StSt returns a hierarchical representation of the text, atomized by glyph, so something like the above string would appear like this when you print it via `txt.tree()`:

    """
    <DPS:2——tag:?/data{}):::glyphName:None>
    | <DPS:6——tag:?/data{}):::glyphName:None>
    | | <DP(typo:int(True)(M))——tag:?/data:{}>
    | | <DP(typo:int(True)(u))——tag:?/data:{}>
    | | <DP(typo:int(True)(l))——tag:?/data:{}>
    | | <DP(typo:int(True)(t))——tag:?/data:{}>
    | | <DP(typo:int(True)(i))——tag:?/data:{}>
    | | <DP(typo:int(True)(hyphen))——tag:?/data:{}>
    | <DPS:4——tag:?/data{}):::glyphName:None>
    | | <DP(typo:int(True)(l))——tag:?/data:{}>
    | | <DP(typo:int(True)(i))——tag:?/data:{}>
    | | <DP(typo:int(True)(n))——tag:?/data:{}>
    | | <DP(typo:int(True)(e))——tag:?/data:{}>
    """

    # If you want the text as a single vector (pen), you can do something like this:

    txt = txt.pen()