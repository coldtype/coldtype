from enum import Enum

try:
    import glfw
except ImportError:
    glfw = None

class KeyboardShortcut(Enum):
    PreviewPrev = "prev_prev"
    PreviewPrevMany = "prev_prev_many"
    PreviewNext = "prev_next"
    PreviewNextMany = "prev_next_many"
    
    ClearLastRender = "clear_last_render"
    ClearRenderedFrames = "clear_rendered_frames"
    
    PlayRendered = "play_rendered"
    PlayPreview = "play_preview"

    ReloadSource = "reload_source"
    RestartApp = "restart_app"
    Quit = "quit"
    Kill = "kill"

    Build = "build"
    Release = "release"
    RenderAll = "render_all"
    RenderOne = "render_one"
    RenderWorkarea = "render_workarea"
    ToggleMultiplex = "toggle_multiplex"

    SetWorkareaIn = "set_workarea_in"
    SetWorkareaOut = "set_workarea_out"
    
    JumpPrev = "jump_prev"
    JumpNext = "jump_next"
    JumpHome = "jump_home"
    JumpEnd = "jump_end"
    JumpStoryboard = "jump_storyboard"

    OverlayInfo = "overlay_info"
    OverlayTimeline = "overlay_timeline"
    OverlayRendered = "overlay_rendered"

    PreviewScaleDown = "preview_scale_down"
    PreviewScaleUp = "preview_scale_up"
    PreviewScaleMin = "preview_scale_min"
    PreviewScaleMax = "preview_scale_max"
    PreviewScaleDefault = "preview_scale_default"

    WindowOpacityDown = "window_opacity_down"
    WindowOpacityUp = "window_opacity_up"
    WindowOpacityMin = "window_opacity_min"
    WindowOpacityMax = "window_opacity_max"

    MIDIControllersPersist = "midi_controllers_persist"
    MIDIControllersClear = "midi_controllers_clear"
    MIDIControllersReset = "midi_controllers_reset"

    JumpToFrameFunctionDef = "jump_to_function_def"
    OpenInEditor = "open_in_editor"
    ShowInFinder = "show_in_finder"

    ViewerTakeFocus = "viewer_take_focus"

    ViewerSoloNone = "viewer_solo_none"
    ViewerSoloNext = "viewer_solo_next",
    ViewerSoloPrev = "viewer_solo_prev",
    ViewerSolo1 = "viewer_solo_1"
    ViewerSolo2 = "viewer_solo_2"
    ViewerSolo3 = "viewer_solo_3"
    ViewerSolo4 = "viewer_solo_4"
    ViewerSolo5 = "viewer_solo_5"
    ViewerSolo6 = "viewer_solo_6"
    ViewerSolo7 = "viewer_solo_7"
    ViewerSolo8 = "viewer_solo_8"
    ViewerSolo9 = "viewer_solo_9"

    ToggleCapturing = "toggle_capturing"
    CaptureOnce = "capture_once"

    CopySVGToClipboard = "copy_svg_to_clipboard"

    LoadNextInDirectory = "load_next_in_directory"
    LoadPrevInDirectory = "load_prev_in_directory"


KeyboardShortcutExplainers = {
    KeyboardShortcut.PreviewPrev:
        "Go to the previous frame",
    KeyboardShortcut.PreviewPrevMany:
        "Go n-frames backward (cycling)",
    KeyboardShortcut.PreviewNext:
        "Go to the next frame",
    KeyboardShortcut.PreviewNextMany:
        "Go n-frames forward (cycling)",
    KeyboardShortcut.ClearLastRender:
        "When compositing, delete the existing framebuffer",
    KeyboardShortcut.ClearRenderedFrames:
        "Delete all the rendered frames on disk for this animation",
    KeyboardShortcut.PlayRendered:
        "Play the rendered-to-disk version of this animation",
    KeyboardShortcut.PlayPreview:
        "Play the current animation as fast as possible, evaluating the code live",
    KeyboardShortcut.RestartApp:
        "Restart the app (a shortcut for when you've modified code that isn't reloaded automatically on save)",
    KeyboardShortcut.Quit:
        "Quit the app and stop the renderer completely (alias of hitting the window X or hitting Ctrl-C in the terminal)",
    KeyboardShortcut.Build:
        "Trigger the custom ``build`` function (if there’s one defined in your code)",
    KeyboardShortcut.Release:
        "Trigger the custom ``release`` function (if there's one defined in your code)",
    KeyboardShortcut.RenderAll:
        "Render all the frames in this animation to disk",
    KeyboardShortcut.RenderOne:
        "Render just the current frame to disk",
    KeyboardShortcut.RenderWorkarea:
        "Render the workarea to disk (if a workarea is defined)",
    KeyboardShortcut.ToggleMultiplex:
        "Toggle multiplexing (multicore rendering) on and off",
    KeyboardShortcut.OverlayInfo:
        "Turn on the “info” overlay",
    KeyboardShortcut.OverlayRendered:
        "Turn on the “rendered” overlay (only used in the blender workflow for previewing a blender-rendered frame)",
    KeyboardShortcut.PreviewScaleDown:
        "Shrink the viewer",
    KeyboardShortcut.PreviewScaleUp:
        "Enlarge the viewer",
    KeyboardShortcut.PreviewScaleMin:
        "Make the viewer as small as possible",
    KeyboardShortcut.PreviewScaleMax:
        "Make the viewer as large as possible",
    KeyboardShortcut.PreviewScaleDefault:
        "Make the viewer the standard size (100%)",
    KeyboardShortcut.WindowOpacityDown:
        "Make the viewer more transparent",
    KeyboardShortcut.WindowOpacityUp:
        "Make the viewer less transparent",
    KeyboardShortcut.WindowOpacityMin:
        "Make the viewer as transparent as possible",
    KeyboardShortcut.WindowOpacityMax:
        "Make the viewer fully opaque",
    KeyboardShortcut.OpenInEditor:
        "Open the currently-rendered file in your code editor",
    KeyboardShortcut.ShowInFinder:
        "Show the renders directory associated with this animation in the finder/explorer/fileviewer",
    KeyboardShortcut.ViewerSoloNone:
        "View all defined renderables and animations",
    KeyboardShortcut.ViewerSoloNext:
        "Solo the “next” animation/renderable in the file",
    KeyboardShortcut.ViewerSoloPrev:
        "Solo the “previous” animation/renderable in the file",
    KeyboardShortcut.ViewerSolo1:
        "Solo the first animation/renderable in the file",
    KeyboardShortcut.ViewerSolo2:
        "Solo the second animation/renderable in the file",
    KeyboardShortcut.ViewerSolo3:
        "Solo the third animation/renderable in the file",
    KeyboardShortcut.CopySVGToClipboard:
        "Copy the current vector to the clipboard as SVG (can be pasted into Illustrator)",
    KeyboardShortcut.LoadNextInDirectory:
        "If you have a directory of coldtype .py files, this will load the next one in the directory (alphabetically), so you can skip stopping and restarting the command-line process with different arguments",
    KeyboardShortcut.LoadPrevInDirectory:
        "If you have a directory of coldtype .py files, this will load the previous one in the directory (alphabetically), so you can skip stopping and restarting the command-line process with different arguments",
}


REPEATABLE_SHORTCUTS = [
    KeyboardShortcut.PreviewPrev,
    KeyboardShortcut.PreviewPrevMany,
    KeyboardShortcut.PreviewNext,
    KeyboardShortcut.PreviewNextMany,
    KeyboardShortcut.PreviewScaleUp,
    KeyboardShortcut.PreviewScaleDown,
    KeyboardShortcut.JumpPrev,
    KeyboardShortcut.JumpNext
]

def symbol_to_glfw(s):
    lookup = {
        "cmd": glfw.MOD_SUPER,
        "ctrl": glfw.MOD_CONTROL,
        "shift": glfw.MOD_SHIFT,
        "alt": glfw.MOD_ALT,
        "<up>": glfw.KEY_UP,
        "<down>": glfw.KEY_DOWN,
        "<left>": glfw.KEY_LEFT,
        "<right>": glfw.KEY_RIGHT,
        "<space>": glfw.KEY_SPACE,
        "<home>": glfw.KEY_HOME,
        "<end>": glfw.KEY_END,
        "<enter>": glfw.KEY_ENTER,
        "-": glfw.KEY_MINUS,
        "=": glfw.KEY_EQUAL,
        "/": glfw.KEY_SLASH,
        "'": glfw.KEY_APOSTROPHE,
        "<backslash>": glfw.KEY_BACKSLASH,
    }
    if s in lookup:
        return lookup[s]
    else:
        k = f"KEY_{s.upper()}"
        if hasattr(glfw, k):
            return getattr(glfw, k)
        elif "np" in s:
            return getattr(glfw, f"KEY_KP_{s[2:]}")
        else:
            raise Exception("Invalid keyboard shortcut symbol", s)


SHORTCUTS = {
    KeyboardShortcut.PreviewPrevMany: [
        [["shift"], "j"],
        [["shift"], "<left>"]
    ],
    KeyboardShortcut.PreviewPrev: [
        [[], "j"],
        [[], "<left>"]
    ],
    KeyboardShortcut.PreviewNextMany: [
        [["shift"], "l"],
        [["shift"], "<right>"]
    ],
    KeyboardShortcut.PreviewNext: [
        [[], "l"],
        [[], "<right>"]
    ],
    
    KeyboardShortcut.ClearLastRender: [
        [[], "<backslash>"]
    ],
    KeyboardShortcut.ClearRenderedFrames: [
        [["shift"], "<backslash>"]
    ],
    
    KeyboardShortcut.PlayRendered: [
        [["shift"], "<space>"],
        #[["shift"], glfw.KEY_K]
    ],
    KeyboardShortcut.PlayPreview: [
        [[], "<space>"],
        #[[], glfw.KEY_K]
    ],

    KeyboardShortcut.ReloadSource: [
        [[], "<enter>"],
        [[], "p"],
    ],
    KeyboardShortcut.RestartApp: [
        [["cmd"], "r"]
    ],
    KeyboardShortcut.Quit: [
        [[], "q"]
    ],

    KeyboardShortcut.Release: [
        [[], "r"],
    ],
    KeyboardShortcut.Build: [
        [[], "b"],
    ],
    KeyboardShortcut.RenderAll: [
        [[], "a"],
    ],
    KeyboardShortcut.RenderOne: [
        [["cmd"], "a"],
    ],
    KeyboardShortcut.RenderWorkarea: [
        [[], "w"]
    ],
    KeyboardShortcut.ToggleMultiplex: [
        [[], "m"]
    ],

    KeyboardShortcut.SetWorkareaIn: [
        [["cmd"], "i"]
    ],
    KeyboardShortcut.SetWorkareaOut: [
        [["cmd"], "o"]
    ],

    KeyboardShortcut.JumpPrev: [
        [[], "<up>"],
        [[], "i"]
    ],
    KeyboardShortcut.JumpNext: [
        [[], "<down>"],
        [[], "k"]
    ],
    KeyboardShortcut.JumpHome: [
        [[], "<home>"],
        [["shift"], "h"]
    ],
    KeyboardShortcut.JumpEnd: [
        [[], "<end>"]
    ],
    KeyboardShortcut.JumpStoryboard: [
        [["cmd"], "<home>"]
    ],

    KeyboardShortcut.OverlayInfo: [
        [[], "/"]
    ],
    KeyboardShortcut.OverlayTimeline: [
        [["cmd"], "t"]
    ],
    KeyboardShortcut.OverlayRendered: [
        [[], "'"]
    ],

    KeyboardShortcut.PreviewScaleUp: [
        [[], "="]
    ],
    KeyboardShortcut.PreviewScaleDown: [
        [[], "-"]
    ],
    KeyboardShortcut.PreviewScaleMin: [
        [["cmd"], "-"]
    ],
    KeyboardShortcut.PreviewScaleMax: [
        [["cmd"], "="]
    ],
    KeyboardShortcut.PreviewScaleDefault: [
        [["cmd"], "0"]
    ],

    KeyboardShortcut.WindowOpacityDown: [
        [["cmd"], "<down>"]
    ],
    KeyboardShortcut.WindowOpacityUp: [
        [["cmd"], "<up>"]
    ],
    KeyboardShortcut.WindowOpacityMin: [
        [["cmd", "shift"], "<down>"],
    ],
    KeyboardShortcut.WindowOpacityMax: [
        [["cmd", "shift"], "<up>"]
    ],

    KeyboardShortcut.JumpToFrameFunctionDef: [
        [[], "f"],
    ],
    KeyboardShortcut.OpenInEditor: [
        [[], "o"]
    ],
    KeyboardShortcut.ShowInFinder: [
        [[], "s"]
    ],

    KeyboardShortcut.ViewerSoloNone: [
        [[], "np0"],
        [[], "0"]
    ],
    KeyboardShortcut.ViewerSoloNext: [
        [["cmd"], "<right>"]
    ],
    KeyboardShortcut.ViewerSoloPrev: [
        [["cmd"], "<left>"]
    ],
    KeyboardShortcut.ViewerSolo1: [
        [[], "np1"],
        [[], "1"]
    ],
    KeyboardShortcut.ViewerSolo2: [
        [[], "np2"],
        [[], "2"]
    ],
    KeyboardShortcut.ViewerSolo3: [
        [[], "np3"],
        [[], "3"]
    ],
    KeyboardShortcut.ViewerSolo4: [
        [[], "np4"],
        [[], "4"]
    ],
    KeyboardShortcut.ViewerSolo5: [
        [[], "np5"],
        [[], "5"]
    ],
    KeyboardShortcut.ViewerSolo6: [
        [[], "np6"],
        [[], "6"]
    ],
    KeyboardShortcut.ViewerSolo7: [
        [[], "np7"],
        [[], "7"]
    ],
    KeyboardShortcut.ViewerSolo8: [
        [[], "np8"],
        [[], "8"]
    ],
    KeyboardShortcut.ViewerSolo9: [
        [[], "np9"],
        [[], "9"]
    ],

    KeyboardShortcut.ToggleCapturing: [
        [["shift"], "c"]
    ],
    KeyboardShortcut.CaptureOnce: [
        [["cmd", "shift"], "c"]
    ],

    KeyboardShortcut.CopySVGToClipboard: [
        [["cmd"], "c"]
    ],

    KeyboardShortcut.LoadNextInDirectory: [
        [["cmd", "alt"], "<right>"]
    ],
    KeyboardShortcut.LoadPrevInDirectory: [
        [["cmd", "alt"], "<left>"]
    ],

    KeyboardShortcut.MIDIControllersPersist: [
        [["cmd"], "m"],
    ],
    KeyboardShortcut.MIDIControllersClear: [
        [["alt"], "m"],
    ],
    KeyboardShortcut.MIDIControllersReset: [
        [["ctrl"], "m"],
    ]
}

def shortcuts_keyed():
    keyed = {}
    for k, v in SHORTCUTS.items():
        modded = []
        for mods, symbol in v:
            modded.append([[symbol_to_glfw(s) for s in mods], symbol_to_glfw(symbol)])
        keyed[k] = modded
    return keyed

if __name__ == "__main__":
    from subprocess import Popen, PIPE

    out = """
Cheatsheet
==========

"""

    for shortcut, key_combos in list(SHORTCUTS.items())[:]:
        name = str(shortcut).split(".")[-1]
        explain = KeyboardShortcutExplainers.get(shortcut)
        if not explain:
            continue
        out += f"* **{name}** (``\"{KeyboardShortcut(shortcut).value}\"``)\n"
        out += ("\n  " + explain + "\n\n")
        for mods, key in key_combos:
            kc = " ".join([*mods, key])
            out += ("  * " + f"``{kc}``\n")
        out += "\n\n"
    
    print(out)

    process = Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=PIPE)
    process.communicate(out.encode("utf-8"))