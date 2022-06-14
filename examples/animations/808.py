# 808 animation
# 📽 You can view this code as an animation here: https://vimeo.com/479376752 📽

# For this animation, we'll need the standard coldtype library as well as some optional bits, the `MidiReader` and the `warp_fn` from the warping library.

from coldtype import *
from coldtype.warping import warp
from coldtype.fx.skia import phototype

# This is the "logo font" for Coldtype, and it's packaged with the library itself

obvs = Font.ColdtypeObviously()

# Here the `MidiReader` comes into play — this is a class that parses midi files and converts the native time values to more useful frame-based time-values, based on a frame-per-second (`fps`) value.

# This is also useful to load before the render function, because this MIDI data doesn’t change once our program is loaded.

wav = __sibling__("media/808.wav")

midi = MidiTimeline(
    __sibling__("media/808.mid")
    , duration=120
    , bpm=120
    , fps=30)

ar = {
    "KD": [5, 50],
    "CW": [15, 75],
    "HT": [10, 10],
    "RS": [5, 5],
    "SD": [10, 40],
    "TM": [5, 10]
}

# I like to keep things like logos in UFO source files, since they aren’t really typographic, so you don’t need to load them as fonts. Here we load a ufo of logos via `DefconFont`, which makes keyed lookups of vectors very easy.

logos = DefconFont("assets/logos.ufo")

# OK, here’s the main render function. To start this off, we'll define variables for `kick` and `cowbell`, since we'll be referencing those when we build the initial text lockup in the next code block.

# The `fv` method is a little cryptic, but we’re looking for `(f)rame-(v)alues` for given MIDI notes, the `[36]` and `[47]` respectively. (Drumkits in Ableton Live usually begin on 36, so that’s usually where you’ll find the kick when reading a MIDI file generated by Ableton.)

@animation(timeline=midi, audio=wav)
def drummachine(f):
    drums = f.t
    kick = drums.ki(36)
    cowbell = drums.ki(47)

    # Now we can build the initial `Style` specification, using the MIDI values for kick and cowbell to control the tracking (`tu`), and the `wdth` of the variable font, via the `.ease()` function available on the object returned from an `.fv` call.

    # We can also re-kern the T/Y for this particular use, since the text is so big, and when it gets stroked later on, we can avoid having a too-large visual mass in the composition. (Also it’s fun to demonstrate that you can easily re-kern fonts with the `kp=` keyword and a dictionary of glyph-name pairs. (`kp` stands for kern-pairs.))

    style = Style(obvs,
        390,
        tu=cowbell.adsr(ar["CW"], r=(-150, 400)),
        wdth=cowbell.adsr(ar["CW"], r=(1, 0.75)),
        ro=1,
        r=1,
        kp={"T/Y":-25})

    # Now with the `style` variable settled, we can construct a multi-line text lockup with the `StSt` class, by passing in a rectangle to hold the lockup, then the text itself, and the style object we created above.

    # We can also set the leading of the multi-line setting here, by specifying `leading=` as a function of the kick signal.
    
    pens = (StSt("COLD\nTYPE", style,
        leading=kick.adsr(ar["KD"], r=(10, 50)))
        .align(f.a.r))

    # So now we’ve got the lockup, and we move from _building_ the text to _messing_ with it, since we converted from the "text" realm to the "vector" realm with that `.pens()` call above. This is analogous to hitting "Convert to Outlines" in Illustrator (except in this case, if we want to change the text later, it’s easy).

    # Anyway, the point is now we have a structured representation of the text that we can query and modify, kind of like manipulating a DOM via css or js if you're familiar with web tech.

    # To start, let’s visualize the snare hits by shearing the line composition & rotating the two letters that correspond to where the snares hit in an 8-count. That's a fancy way of saying, the eight letters here correspond to the 8 eighth-notes in the bar, so we want to modify letters 3 and 7 (aka `P` and `L`), which correspond to the snare hits.

    # A few notes:

    # - `ffg` stands for `find-first-glyph`, which finds the first glyph with the given name. So we want to find the L in the first line of text, that’s `pens[0].ffg("L")`; we want to find the P on the second line, that’s `pens[1].ffg("P")`, etc.

    # - `î` (aka index) allows you to modify a nested pen value in-place as a set of contours with a callback function (aka a `lambda`). Basically, the `î` function first "explodes" the glyph into all its component contours (in the P’s case, that’s the outer shape & the counter shape), and then gives you an opportunity to modify just the specified contour (at the "index") before reassembling the contours into the letter (so the counter is still a counter and not just another filled-in shape). That’s how we’re able to keep the counter of the P frozen in place. If we got rid of the `î` call and instead rotated the P glyph itself (ala `pens[1].ffg("P").rotate(rim.ease()*-270)`), then the counter shape would also rotate.

    snare = drums.ki(40)
    se, si = snare.adsr(ar["SD"], find=1)

    if si == 0: # the first snare hit
        pens[0].translate(-150*se, 0)
        pens[1].translate(150*se, 0)
        pens[0].ffg("L").rotate(se*-270)
    else: # the second snare hit
        pens[0].translate(150*se, 0)
        pens[1].translate(-150*se, 0)
        pens[1].ffg("P").î(0, lambda p: p.rotate(se*270))

    # Whew, ok that was a little complicated. Now let’s do something similar with `î` on the P, but this time rotate just the counter shape when the second rimshot hits (we can ignore the first rimshot b/c it hits at the same time as a hi-hat, which we'll visualize in a second).

    rim = drums.ki(39)
    re, ri = rim.adsr(ar["RS"], rng=(0, -270), find=1)

    if ri == 1:
        pens[1].ffg("P").î(1, lambda p: p.rotate(re))

    # Wouldn’t it be cool if the letters corresponding to the kicks scaled up whenever the kick hit? That’s what’s happening here, along with a more programmer-y idiom, i.e. unpacking a tuple to the `line, glyph`. This is just a way of abbreviating a longer `if-else` statement that would contain redundant code.

    ke, ki = kick.adsr(ar["KD"], rng=(1, 1.5), find=1)
    line, glyph = (0, "C") if ki == 0 else (1, "Y")
    (pens[line]
        .ffg(glyph)
        .scale(ke))

    # OK, on to the hi-hats. Here we get the hat signal from the midi, with an even preverb-reverb (that’s the `[10, 10]` bit), because we want to mimic the regular action of a drummer hitting a hi-hat.

    hat = drums.ki(43)
    he, hi = hat.adsr(ar["HT"], find=1)

    # When the first hat hits, let’s move the counter in the O to the right.

    if hi == 0:
        (pens[0].ffg("O")
            .î(1, lambda p: p.translate(80*he, 0)))

    # And when the second hat hits, let’s move the counter of the D in the first line, this time translating it down & then rotating it, to make it seem like it’s falling and then bouncing back up from the bottom of the outer shape.

    elif hi == 1:
        (pens[0].ffg("D")
            .î(1, lambda p: p.translate(-30*he, -100*he).rotate(he*110)))

    # And when the third and fourth hats hit, let’s move the left and right sides of the T crossbar, via the `ï` (indices) function, which lets you adjust the x and y values of a certain set of points (at the given indices) directly via a callback.

    elif hi == 2:
        pens[1].ffg("T").ï(range(0, 7), lambda p: p.o(-150*he, 0))
    elif hi == 3:
        pens[1].ffg("T").ï(range(26, 35), lambda p: p.o(150*he, 0))

    # Ok last hat! Here we exaggerate the horizontality of the E counters with the same `ï` function.

    elif hi == 4:
        (pens[1].ffg("E")
            .ï(range(10, 15), lambda p: p.o(-35*he, 0))
            .ï(range(23, 30), lambda p: p.o(-75*he, 0)))

    # The last visualization is the tom-tom hit. Here we can just nudge up the outer contour of the O in the first line.

    tom = (drums.ki(50)
        .adsr(ar["TM"], rng=(0, -80)))

    (pens[0].ffg("O").î(0, lambda p: p.translate(0, tom)))

    # And a little branding: load the Goodhertz logo from the ufo via `glyph` and apply a `warp` to it, using the `warp` chainable. This lets you quickly & easily apply a "wavey" Perlin noise transform. To be honest I barely understand how it works, but it looks cool.

    ghz_logo = (P()
        .glyph(logos["goodhertz_logo_2019"])
        .scale(0.2)
        .align(f.a.r, y="mny")
        .translate(0, 100)
        .ch(warp(None, speed=f.e("l", 1, rng=(0, 3)), rz=3, mult=50))
        .skew(cowbell.adsr(ar["CW"], rng=(0, 0.5))))

    # Now we return the data we’ve manipulated to the renderer. This is also where we apply the finishing touches to the `COLD\nTYPE` lockup, by reversing the lines so that the the first line is last (meaning it shows up on top, which is nice for when the C gets really big), and then by applying an `understroke`, which interleaves stroked copies of each letter in the composition, giving us a classic look that we can hit with a high-contrast `phototype` simulation. And then we’re done!

    return PS([
        P(f.a.r).f(0),
        ghz_logo.f(hsl(0.9, 0.55, 0.5)),
        (pens.fssw(1, 0, 15, 1)
            .reverse()
            .translate(0, 100)
            .ch(phototype(f.a.r, cut=190, cutw=8)))])