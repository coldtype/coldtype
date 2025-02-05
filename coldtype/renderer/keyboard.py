import platform
from enum import Enum

try:
    import glfw
except ImportError:
    glfw = None


LAYOUT_REMAPS = {
    "tr": {73: 73, 39: 73, 47: 46},
    "kk": {54: 44, 55: 46},
    "de": {89: 90, 47: 45},
    "ru": {47: 46},
    "uk": {47: 46},
    "it": {47: 45},
    "dvorak": {81: 39, 69: 46, 82: 80, 84: 89, 89: 70, 85: 71, 73: 67, 79: 82, 80: 76, 93: 47, 91: 61, 83: 79, 70: 85, 71: 73, 72: 68, 74: 72, 75: 84, 76: 78, 39: 45, 88: 81, 67: 74, 86: 75, 66: 88, 44: 87, 46: 86, 47: 90, 45: 93, 61: 91},
    "fr": {81: 65, 87: 90, 65: 81, 77: 44, 44: 59},
    "he": {81: 47, 87: 39, 93: 91, 91: 93, 39: 44, 47: 46},
    "gr": {81: 59},
    "cs": {45: 61, 89: 90, 47: 45},
    "by": {91: 39, 47: 46},
    "sv": {47: 45},
    "colemak": {69: 70, 82: 80, 84: 71, 89: 74, 85: 76, 73: 85, 79: 89, 80: 59, 83: 82, 70: 84, 71: 68, 74: 78, 75: 69, 76: 73},
    "es": {47: 45, 45: 39},
}


class KeyboardShortcut(Enum):
    PreviewPrev = "prev_prev"
    PreviewPrevMany = "prev_prev_many"
    PreviewNext = "prev_next"
    PreviewNextMany = "prev_next_many"
    
    ClearLastRender = "clear_last_render"
    ClearRenderedFrames = "clear_rendered_frames"
    ResetInitialMemory = "reset_initial_memory"
    ResetMemory = "reset_memory"
    
    PlayRendered = "play_rendered"
    PlayPreview = "play_preview"
    PlayToEnd = "play_to_end"

    Echo = "echo"

    ReloadSource = "reload_source"
    RestartApp = "restart_app"
    Quit = "quit"
    Kill = "kill"
    Sleep = "sleep"

    Build = "build"
    Release = "release"
    RenderAll = "render_all"
    RenderOne = "render_one"
    RenderFrom = "render_from"
    RenderWorkarea = "render_workarea"
    RenderDirectory = "render_directory"
    RenderAllAndPlay = "render_all_and_play"
    RenderAllAndRelease = "render_all_and_release"
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
    OverlayRecording = "overlay_recording"
    EnableAudio = "toggle_audio"
    ToggleTimeViewer = "toggle_time_viewer"
    ToggleUI = "toggle_ui"
    ToggleXray = "toggle_xray"
    ToggleGrid = "toggle_grid"
    CycleVersionsForward = "cycle_versions_forward"
    CycleVersionsBack = "cycle_versions_back"

    PreviewScaleDown = "preview_scale_down"
    PreviewScaleUp = "preview_scale_up"
    PreviewScaleMin = "preview_scale_min"
    PreviewScaleMax = "preview_scale_max"
    PreviewScaleDefault = "preview_scale_default"

    WindowOpacityDown = "window_opacity_down"
    WindowOpacityUp = "window_opacity_up"
    WindowOpacityMin = "window_opacity_min"
    WindowOpacityMax = "window_opacity_max"

    ViewerPlaybackSpeedIncrease = "viewer_playback_speed_increase"
    ViewerPlaybackSpeedDecrease = "viewer_playback_speed_decrease"
    ViewerPlaybackSpeedReset = "viewer_playback_speed_reset"

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
    ViewerSoloFirst = "viewer_solo_first",
    ViewerSoloLast = "viewer_solo_last",
    ViewerSolo1 = "viewer_solo_1"
    ViewerSolo2 = "viewer_solo_2"
    ViewerSolo3 = "viewer_solo_3"
    ViewerSolo4 = "viewer_solo_4"
    ViewerSolo5 = "viewer_solo_5"
    ViewerSolo6 = "viewer_solo_6"
    ViewerSolo7 = "viewer_solo_7"
    ViewerSolo8 = "viewer_solo_8"
    ViewerSolo9 = "viewer_solo_9"

    PrintApproxFPS = "show_approx_fps"

    ViewerSampleFrames1 = "viewer_sample_frames_1"
    ViewerSampleFrames2 = "viewer_sample_frames_2"
    ViewerSampleFrames3 = "viewer_sample_frames_3"
    ViewerSampleFrames4 = "viewer_sample_frames_4"
    ViewerSampleFrames5 = "viewer_sample_frames_5"
    ViewerSampleFrames6 = "viewer_sample_frames_6"
    ViewerSampleFrames7 = "viewer_sample_frames_7"
    ViewerSampleFrames8 = "viewer_sample_frames_8"
    ViewerSampleFrames9 = "viewer_sample_frames_9"

    ViewerNumberedAction1 = "viewer_numbered_action_1"
    ViewerNumberedAction2 = "viewer_numbered_action_2"
    ViewerNumberedAction3 = "viewer_numbered_action_3"
    ViewerNumberedAction4 = "viewer_numbered_action_4"
    ViewerNumberedAction5 = "viewer_numbered_action_5"
    ViewerNumberedAction6 = "viewer_numbered_action_6"
    ViewerNumberedAction7 = "viewer_numbered_action_7"
    ViewerNumberedAction8 = "viewer_numbered_action_8"
    ViewerNumberedAction9 = "viewer_numbered_action_9"

    ToggleCapturing = "toggle_capturing"
    CaptureOnce = "capture_once"

    CopySVGToClipboard = "copy_svg_to_clipboard"
    TogglePrintResult = "toggle_print_result"
    PrintResultOnce = "print_result_once"

    LoadNextInDirectory = "load_next_in_directory"
    LoadPrevInDirectory = "load_prev_in_directory"

    TestDirectory = "test_directory"


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
    KeyboardShortcut.ResetInitialMemory:
        "When using dynamic memory, this resets it to the initial state defined in the decorator",
    KeyboardShortcut.ResetMemory:
        "When using dynamic memory, this calls the reset_memory function passed to the decorator",
    KeyboardShortcut.PlayRendered:
        "Play the rendered-to-disk version of this animation",
    KeyboardShortcut.PlayPreview:
        "Play the current animation as fast as possible, evaluating the code live",
    KeyboardShortcut.PlayToEnd:
        "Same as PlayPreview, but will not loop",
    KeyboardShortcut.Echo:
        "Play a sound",
    KeyboardShortcut.EnableAudio:
        "If audio is defined on a renderable, toggle whether or not to play it",
    KeyboardShortcut.RestartApp:
        "Restart the app (a shortcut for when you've modified code that isn't reloaded automatically on save)",
    KeyboardShortcut.Quit:
        "Quit the app and stop the renderer completely (alias of hitting the window X or hitting Ctrl-C in the terminal)",
    KeyboardShortcut.Build:
        "Trigger the custom `build` function (if there’s one defined in your code)",
    KeyboardShortcut.Release:
        "Trigger the custom `release` function (if there's one defined in your code)",
    KeyboardShortcut.RenderAll:
        "Render all the frames in this animation to disk",
    KeyboardShortcut.RenderAllAndPlay:
        "Render all the frames in this animation to disk, then start a looped playback of the rendered frames",
    KeyboardShortcut.RenderAllAndRelease:
        "Render all the frames in this animation to disk, then run the custom release function",
    KeyboardShortcut.RenderOne:
        "Render just the current frame to disk",
    KeyboardShortcut.RenderFrom:
        "Render all the frames starting with the current one",
    KeyboardShortcut.RenderWorkarea:
        "Render the workarea to disk (if a workarea is defined)",
    KeyboardShortcut.RenderDirectory:
        "Cycle adjacents and render all in each",
    KeyboardShortcut.ToggleMultiplex:
        "Toggle multiplexing (multicore rendering) on and off",
    KeyboardShortcut.OverlayInfo:
        "Turn on the “info” overlay",
    KeyboardShortcut.OverlayRendered:
        "Turn on the “rendered” overlay (only used in the blender workflow for previewing a blender-rendered frame)",
    KeyboardShortcut.OverlayRecording:
        "Turn on the “recording” overlay",
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
    KeyboardShortcut.TogglePrintResult:
        "Print the tree representation of what's being returned to the renderer",
    KeyboardShortcut.PrintResultOnce:
        "Print the tree representation of what's being returned to the renderer",
    KeyboardShortcut.LoadNextInDirectory:
        "If you have a directory of coldtype .py files, this will load the next one in the directory (alphabetically), so you can skip stopping and restarting the command-line process with different arguments",
    KeyboardShortcut.LoadPrevInDirectory:
        "If you have a directory of coldtype .py files, this will load the previous one in the directory (alphabetically), so you can skip stopping and restarting the command-line process with different arguments",
    KeyboardShortcut.TestDirectory:
        "Test everything in the directory",
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
    GLFW_SPECIALS_LOOKUP = {
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
        "<page-up>": glfw.KEY_PAGE_UP,
        "<page-down>": glfw.KEY_PAGE_DOWN,
        "<tab>": glfw.KEY_TAB,
        ",": glfw.KEY_COMMA,
        ".": glfw.KEY_PERIOD,
        "-": glfw.KEY_MINUS,
        "=": glfw.KEY_EQUAL,
        "/": glfw.KEY_SLASH,
        "'": glfw.KEY_APOSTROPHE,
        ";": glfw.KEY_SEMICOLON,
        "<backslash>": glfw.KEY_BACKSLASH,
        "<bracket-right>": glfw.KEY_RIGHT_BRACKET,
        "<bracket-left>": glfw.KEY_LEFT_BRACKET,
    }
    if s in GLFW_SPECIALS_LOOKUP:
        return GLFW_SPECIALS_LOOKUP[s]
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
    KeyboardShortcut.ResetInitialMemory: [
        [[], "<bracket-right>"]
    ],
    KeyboardShortcut.ResetMemory: [
        [[], "<bracket-left>"]
    ],
    
    KeyboardShortcut.PlayRendered: [
        [["shift"], "<space>"],
        #[["shift"], glfw.KEY_K]
    ],
    KeyboardShortcut.PlayPreview: [
        [[], "<space>"],
        #[[], glfw.KEY_K]
    ],
    KeyboardShortcut.PlayToEnd: [
        [[], "e"]
    ],
    KeyboardShortcut.Echo: [
        [["shift"], "e"]
    ],
    KeyboardShortcut.EnableAudio: [
        [[], "."]
    ],

    KeyboardShortcut.ReloadSource: [
        [[], "<enter>"],
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
    KeyboardShortcut.RenderAllAndPlay: [
        [["shift"], "a"],
    ],
    KeyboardShortcut.RenderAllAndRelease: [
        [["shift", "cmd"], "a"],
    ],
    KeyboardShortcut.RenderDirectory: [
        [["shift", "cmd", "alt"], "a"],
    ],
    KeyboardShortcut.RenderOne: [
        [["cmd"], "a"],
    ],
    KeyboardShortcut.RenderFrom: [
        [["alt"], "a"],
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
        [[], "'"],
        [[], ","],
    ],
    KeyboardShortcut.OverlayRecording: [
        [[], "<tab>"],
    ],

    KeyboardShortcut.ToggleTimeViewer: [
        [[], "v"],
    ],
    KeyboardShortcut.ToggleUI: [
        [["shift"], "u"],
    ],
    KeyboardShortcut.ToggleXray: [
        [[], "x"],
    ],
    KeyboardShortcut.ToggleGrid: [
        [[], "g"],
    ],

    KeyboardShortcut.CycleVersionsForward: [
        [["shift"], "v"],
        [["shift"], "<up>"],
    ],

    KeyboardShortcut.CycleVersionsBack: [
        [["shift"], "<down>"],
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

    KeyboardShortcut.ViewerPlaybackSpeedDecrease: [
        [["shift"], "-"]
    ],
    KeyboardShortcut.ViewerPlaybackSpeedIncrease: [
        [["shift"], "="]
    ],
    # KeyboardShortcut.ViewerPlaybackSpeedReset: [
    #     [["shift"], "0"]
    # ],

    KeyboardShortcut.WindowOpacityDown: [
        [["cmd", "shift"], "<down>"]
    ],
    KeyboardShortcut.WindowOpacityUp: [
        [["cmd", "shift"], "<up>"]
    ],
    KeyboardShortcut.WindowOpacityMin: [
        [["cmd", "shift", "alt"], "<down>"],
    ],
    KeyboardShortcut.WindowOpacityMax: [
        [["cmd", "shift", "alt"], "<up>"]
    ],



    KeyboardShortcut.JumpToFrameFunctionDef: [
        [["cmd"], "f"],
    ],
    KeyboardShortcut.OpenInEditor: [
        [[], "o"]
    ],
    KeyboardShortcut.ShowInFinder: [
        [[], "s"]
    ],

    KeyboardShortcut.ViewerSoloNone: [
        [["shift"], "np0"],
        [["shift"], "0"]
    ],
    KeyboardShortcut.ViewerSoloNext: [
        [["cmd"], "<right>"]
    ],
    KeyboardShortcut.ViewerSoloPrev: [
        [["cmd"], "<left>"]
    ],
    KeyboardShortcut.ViewerSoloFirst: [
        [["cmd"], "<up>"]
    ],
    KeyboardShortcut.ViewerSoloLast: [
        [["cmd"], "<down>"]
    ],
    KeyboardShortcut.ViewerSolo1: [
        [["shift"], "np1"],
        [["shift"], "1"]
    ],
    KeyboardShortcut.ViewerSolo2: [
        [["shift"], "np2"],
        [["shift"], "2"]
    ],
    KeyboardShortcut.ViewerSolo3: [
        [["shift"], "np3"],
        [["shift"], "3"]
    ],
    KeyboardShortcut.ViewerSolo4: [
        [["shift"], "np4"],
        [["shift"], "4"]
    ],
    KeyboardShortcut.ViewerSolo5: [
        [["shift"], "np5"],
        [["shift"], "5"]
    ],
    KeyboardShortcut.ViewerSolo6: [
        [["shift"], "np6"],
        [["shift"], "6"]
    ],
    KeyboardShortcut.ViewerSolo7: [
        [["shift"], "np7"],
        [["shift"], "7"]
    ],
    KeyboardShortcut.ViewerSolo8: [
        [["shift"], "np8"],
        [["shift"], "8"]
    ],
    KeyboardShortcut.ViewerSolo9: [
        [["shift"], "np9"],
        [["shift"], "9"]
    ],

    KeyboardShortcut.PrintApproxFPS: [
        [[], "f"],
    ],

    KeyboardShortcut.ViewerSampleFrames1: [
        [["cmd"], "np1"],
        [["cmd"], "1"]
    ],
    KeyboardShortcut.ViewerSampleFrames2: [
        [["cmd"], "np2"],
        [["cmd"], "2"]
    ],
    KeyboardShortcut.ViewerSampleFrames3: [
        [["cmd"], "np3"],
        [["cmd"], "3"]
    ],
    KeyboardShortcut.ViewerSampleFrames4: [
        [["cmd"], "np4"],
        [["cmd"], "4"]
    ],
    KeyboardShortcut.ViewerSampleFrames5: [
        [["cmd"], "np5"],
        [["cmd"], "5"]
    ],
    KeyboardShortcut.ViewerSampleFrames6: [
        [["cmd"], "np6"],
        [["cmd"], "6"]
    ],
    KeyboardShortcut.ViewerSampleFrames7: [
        [["cmd"], "np7"],
        [["cmd"], "7"]
    ],
    KeyboardShortcut.ViewerSampleFrames8: [
        [["cmd"], "np8"],
        [["cmd"], "8"]
    ],
    KeyboardShortcut.ViewerSampleFrames9: [
        [["cmd"], "np9"],
        [["cmd"], "9"]
    ],


    KeyboardShortcut.ViewerNumberedAction1: [
        [[], "np1"],
        [[], "1"]
    ],
    KeyboardShortcut.ViewerNumberedAction2: [
        [[], "np2"],
        [[], "2"]
    ],
    KeyboardShortcut.ViewerNumberedAction3: [
        [[], "np3"],
        [[], "3"]
    ],
    KeyboardShortcut.ViewerNumberedAction4: [
        [[], "np4"],
        [[], "4"]
    ],
    KeyboardShortcut.ViewerNumberedAction5: [
        [[], "np5"],
        [[], "5"]
    ],
    KeyboardShortcut.ViewerNumberedAction6: [
        [[], "np6"],
        [[], "6"]
    ],
    KeyboardShortcut.ViewerNumberedAction7: [
        [[], "np7"],
        [[], "7"]
    ],
    KeyboardShortcut.ViewerNumberedAction8: [
        [[], "np8"],
        [[], "8"]
    ],
    KeyboardShortcut.ViewerNumberedAction9: [
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
    KeyboardShortcut.TogglePrintResult: [
        [["shift"], "p"]
    ],
    KeyboardShortcut.PrintResultOnce: [
        [[], "p"]
    ],

    KeyboardShortcut.LoadNextInDirectory: [
        [["cmd", "alt"], "<right>"],
        [[], "<page-down>"],
        [[], "u"],
    ],
    KeyboardShortcut.LoadPrevInDirectory: [
        [["cmd", "alt"], "<left>"],
        [[], "<page-up>"],
        [[], "y"],
    ],

    KeyboardShortcut.TestDirectory: [
        [["shift"], "t"]
    ],

    KeyboardShortcut.MIDIControllersPersist: [
        [["cmd"], "m"],
    ],
    KeyboardShortcut.MIDIControllersClear: [
        [["alt"], "m"],
    ],
    KeyboardShortcut.MIDIControllersReset: [
        [["shift"], "m"],
    ]
}

def shortcuts_keyed():
    keyed = {}
    for k, v in SHORTCUTS.items():
        modded = []
        for mods, symbol in v:
            modded.append([[symbol_to_glfw(s) for s in mods], symbol_to_glfw(symbol), symbol])
            if "cmd" in mods:
                mod_mods = ["ctrl" if mod == "cmd" else mod for mod in mods]
                modded.append([[symbol_to_glfw(s) for s in mod_mods], symbol_to_glfw(symbol), symbol])
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
        out += f"* **{name}** (`\"{KeyboardShortcut(shortcut).value}\"`)\n"
        out += ("\n  " + explain + "\n\n")
        for mods, key in key_combos:
            kc = " ".join([*mods, key])
            out += ("  * " + f"`{kc}`\n")
        out += "\n\n"
    
    print(out)

    process = Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=PIPE)
    process.communicate(out.encode("utf-8"))