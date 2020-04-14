from coldtype import *
from coldtype.animation.midi import MidiReader
from coldtype.warping import warp_fn
import noise

# Load the designspace directly (no need for fonts)
obvs = Font("ç/ColdtypeObviously.designspace")

# Load the MIDI before our render, since this won’t change between renders
drums = MidiReader("examples/media/808.mid", duration=120, bpm=120)[0]

# Load our logos ufo for branding-purposes
# (N.B. here we are loading a defcon.Font directly, since the logos.ufo
# isn’t really a font even in spirit)
logos = raw_ufo("ç/logos.ufo")


@animation(duration=drums.duration, bg=0.2, storyboard=[56])
def render(f):
    # Get the kick and cowbell values b/c we’re going to use
    # these in the initial lockup
    kick = drums.fv(f.i, [36], [5, 50])
    cowbell = drums.fv(f.i, [47], [15, 75])

    ### INITIAL LOCKUP
    # Use the `Graf` to set two StyledStrings vertically
    # Adjust the tracking (via `tu` (a shortcut for (t)racking-in-font-(u)nits))
    # using the cowbell midi note, using standard easing
    # also rekern the T & Y together to be a little closer (via the (k)ern-(p)airs)
    # so when they get stroked they don’t create an overly black visual mass
    style = Style(obvs, 390, tu=-150+550*cowbell.ease(), wdth=1-cowbell.ease()*0.75, ro=1, r=1, kp={"T/Y":-25})
    strings = [StyledString(t, style) for t in ["COLD", "TYPE"]]
    pens = Graf(strings, f.a.r, leading=math.floor(kick.ease()*50)).pens().align(f.a.r)

    ### SNARE (+claps)
    # Visualize the snare hits by shearing the line composition
    # & rotating the two letters that correspond to where the snares hit in an 8-count
    snare = drums.fv(f.i, [40], [10, 40])
    if snare.count == 1:
        pens[0].translate(-150*snare.ease(), 0)
        pens[1].translate(150*snare.ease(), 0)
        pens[0].ffg("L").rotate(snare.ease()*-270)
    else:
        pens[0].translate(150*snare.ease(), 0)
        pens[1].translate(-150*snare.ease(), 0)
        # Rotate the outer P shape w/o moving the counter
        pens[1].ffg("P").mod_contour(0, lambda c: c.rotate(snare.ease()*270))

    ### RIMSHOT
    # When the second rim hits (we ignore the first one b/c it’s in sync with a hat (see below)),
    # let’s rotate the P’s counter
    rim = drums.fv(f.i, [39], [5, 5])
    if rim.count == 2:
        pens[1].ffg("P").mod_contour(1, lambda c: c.rotate(rim.ease()*-270))

    ### BIG KICKS
    # Use the kick signal to scale up some letters
    line, glyph = (0, "C") if kick.count == 1 else (1, "Y")
    pens[line].ffg(glyph).scale(1+0.5*kick.ease())
    
    ### HI-HATS
    # Definitely the most complicated bit of all the code:
    # Get the hat signal from the midi, with an even preverb-reverb (10, 10)
    # To mimic the regular action of a drummer hitting a hi-hat
    hat = drums.fv(f.i, [43], [10, 10])
    
    # For the first hat, move the counter of the O in the first line
    if hat.count == 1:
        pens[0].ffg("O").mod_contour(1, lambda c: c.translate(80*hat.ease(), 0))
    
    # For the second hat, move the counter of the D in the first line
    # This time make it a little fancier, first translating it down
    # & then rotating it as well, to make it seem like it's falling
    # and then bouncing back up from the bottom of the outer shape
    elif hat.count == 2:
        pens[0].ffg("D").mod_contour(1, lambda c: c.translate(-30*hat.ease(), -100*hat.ease()).rotate(hat.ease()*110))
    
    # And now for our most complicated trick...
    # Move the T crossbar, first on the left-hand side (hat 3)
    # And then on the right-hand side (hat 4)
    elif hat.count in [3, 4]:
        def move_t_top(idx, x, y):
            if hat.count == 3 and 0 <= idx <= 6:
                return x-150*hat.ease(), y
            elif hat.count == 4 and 22 <= idx <= 30:
                return x+150*hat.ease(), y
        pens[1].ffg("T").map_points(move_t_top)
    
    # Finally (for the hats), exaggerate the horizontality of the E counters
    elif hat.count == 5:
        def move_e_contour(idx, x, y):
            if 9 <= idx <= 13 or 20 <= idx <= 25:
                x -= 50*hat.ease()
            if 0 <= idx <= 33:
                y -= 50*hat.ease()
            return x, y
        pens[1].ffg("E").map_points(move_e_contour)#.translate(hat.ease()*150, 0)

    ### TOMTOM
    # And lastly, use the tom signal to push up the outside of the O in the first line
    tom = drums.fv(f.i, [50], [5, 10])
    pens[0].ffg("O").mod_contour(0, lambda c: c.translate(0, -150*tom.ease()))

    ### BRANDING
    fp = f.a.prg(f.i, easefn="linear").e
    ghz_logo = DATPen().glyph(logos["goodhertz_logo_2019"])
    ghz_logo.scale(0.2).align(f.a.r, y="mny").translate(0, 100).nonlinear_transform(warp_fn(speed=fp*3, rz=3, mult=10))

    # return both elements to the renderer
    return [
        ghz_logo.f(1, 0, 0).skew(cowbell.ease()*1),
        pens.f(0, 1, 0).reversePens().understroke(s=(0, 0, 1), sw=15).translate(0, 100)
    ]