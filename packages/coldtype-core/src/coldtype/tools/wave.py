from coldtype import *
from coldtype.tool import Tool
from coldtype.blender import *


# coldtype-embedded-profile b3dlo_nofile


@b3d_runnable(playback=B3DPlayback.KeepPlaying)
def setup(bw:BpyWorld):
    bw.delete_previous(materials=False)


@b3d_animation(timeline=60, center=(0, 1), upright=1)
def wave(f):
    font = Font.Cacheable(tool.state["font"])
    vars = font.variations()
    vars_keys = list(vars.keys())
    
    axes_order = tool.state.get("axesOrder")
    if axes_order == "auto":
        axes_order = vars_keys
    else:
        axes_order = [x.strip() for x in axes_order.split(",")]
        vars_keys = [x.replace("-", "") for x in axes_order]
    
    ec = tool.state["easing"]

    def glyph(g):
        _vars = {}
        for idx, axis in enumerate(axes_order):
            _vars[axis] = f.adj((idx*2)-g.i*(5+idx)).e(ec, 1)
        return Style(font, 375, variations=_vars)

    return (P(
        Glyphwise(tool.state["text"], glyph, multiline=1)
            .xalign(f.a.r)
            .track(50, v=1)
            .align(f.a.r.drop(100, "S"))
            .mapv(lambda i, p: p
                .removeOverlap()
                .ch(b3d(lambda bp: bp
                    .extrude(f.adj(-i*5).e(ec, 1, rng=(0.1, 1.75))))))))


tool = Tool(ººinputsºº, dict(
    font=[Font.MutatorSans(), str, None, "Font search string"],
    text=["ABC", str, None, "Text to display"],
    easing=["seio", str, None, "Easing curve to use"],
    axesOrder=["auto", str, None, "Order of the axes (default is 'auto', i.e. how they show up in the font); can prefix axis name with - to reverse its appearance in cube"],
    #outline=[0, int, None, "Should there be an outline?"]
    )
    , ui=ººuiºº
    , name="NoordzijCube"
    , doc="Displays a Noordzij cube"
    , blender_runnable=setup)
