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
    PlayPreviewSlow = "play_preview_slow"
    PlayAudioFrame = "play_audio_frame"

    ReloadSource = "reload_source"
    RestartApp = "restart_app"
    Quit = "quit"
    Kill = "kill"

    Build = "build"
    Release = "release"
    RenderAll = "render_all"
    RenderWorkarea = "render_workarea"
    ToggleMultiplex = "toggle_multiplex"

    SetWorkareaIn = "set_workarea_in"
    SetWorkareaOut = "set_workarea_out"
    
    JumpPrev = "jump_prev"
    JumpNext = "jump_next"
    JumpHome = "jump_home"
    JumpEnd = "jump_end"
    JumpStoryboard = "jump_storyboard"

    KeylayerEditing = "keylayer_editing"
    KeylayerCmd = "keylayer_command"
    KeylayerText = "keylayer_text"
    OverlayInfo = "overlay_info"
    OverlayTimeline = "overlay_timeline"

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
    KeyboardShortcut.PlayAudioFrame: [
        [[], "h"]
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

    KeyboardShortcut.KeylayerEditing: [
        [[], "d"]
    ],
    KeyboardShortcut.KeylayerCmd: [
        [[], "c"],
    ],
    KeyboardShortcut.KeylayerText: [
        [[], "t"],
    ],

    KeyboardShortcut.OverlayInfo: [
        [[], "/"]
    ],
    KeyboardShortcut.OverlayTimeline: [
        [["cmd"], "t"]
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
    ]
}