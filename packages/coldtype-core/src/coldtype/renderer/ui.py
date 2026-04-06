from collections import defaultdict
from coldtype.renderable import renderable, ui, animation
from coldtype.text.composer import StSt, Font, Rect, Point, Style
from coldtype.timing.timeline import Timeline
from coldtype.timing.midi import MidiTimeline
from coldtype.runon.path import P
from coldtype.color import bw, hsl
from coldtype.renderer.keyboard import KeyboardShortcut, SHORTCUTS
from functools import partial

def uiView(_renderable):
    r = Rect(max(1080, _renderable.rect.w), 80)

    shortcuts = [[
        KeyboardShortcut.ShowInFinder,
        KeyboardShortcut.RenderAll,
        KeyboardShortcut.OpenInEditor,
        KeyboardShortcut.Quit,
    ]]

    if isinstance(_renderable, animation):
        r = Rect(r.w, r.h+80)
        shortcuts.append([
            KeyboardShortcut.PlayPreview,
            KeyboardShortcut.Release,
            KeyboardShortcut.ToggleTimeViewer,
            KeyboardShortcut.ToggleUI,
        ])

    @renderable(r, bg=0, preview_only=1)
    def _uiView(r):
        rows = r.subdivide_with_leading(len(shortcuts), 2, "N")

        def btn(ri, x):
            ks:KeyboardShortcut = shortcuts[ri][x.i]
            shortcut = SHORTCUTS[ks][0]
            mods = "+".join(shortcut[0])
            if mods:
                keys = mods + "+" + shortcut[1]
            else:
                keys = shortcut[1]

            return (P(
                StSt(ks.name, Font.JBMono(), 24, wght=0.25).f(1),
                StSt(keys, Font.JBMono(), 24, wght=1).f(1)
                )
                .stack(12)
                .align(x.el.inset(14), "W")
                .insert(0, P(x.el).f(0.2)))
        
        def row(x):
            rs = x.el.subdivide_with_leading(4, 2, "W")
            return P().enumerate(rs, partial(btn, x.i))

        return P().enumerate(rows, row)

    return _uiView