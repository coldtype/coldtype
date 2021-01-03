import glfw
from enum import Enum


class KeyboardShortcut(Enum):
    PreviewPrev = "prev_prev"
    PreviewPrevMany = "prev_prev_many"
    PreviewNext = "prev_next"
    PreviewNextMany = "prev_next_many"
    
    ClearLastRender = "clear_last_render"
    
    PlayRendered = "play_rendered"
    PlayPreview = "play_preview"
    PlayAudioFrame = "play_audio_frame"

    ReloadSource = "reload_source"
    RestartApp = "restart_app"
    Quit = "quit"

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


SHORTCUTS = {
    KeyboardShortcut.PreviewPrevMany: [
        [[glfw.MOD_SHIFT], glfw.KEY_J],
        [[glfw.MOD_SHIFT], glfw.KEY_LEFT]
    ],
    KeyboardShortcut.PreviewPrev: [
        [[], glfw.KEY_J],
        [[], glfw.KEY_LEFT]
    ],
    KeyboardShortcut.PreviewNextMany: [
        [[glfw.MOD_SHIFT], glfw.KEY_L],
        [[glfw.MOD_SHIFT], glfw.KEY_RIGHT]
    ],
    KeyboardShortcut.PreviewNext: [
        [[], glfw.KEY_L],
        [[], glfw.KEY_RIGHT]
    ],
    
    KeyboardShortcut.ClearLastRender: [
        [[], glfw.KEY_BACKSLASH]
    ],
    
    KeyboardShortcut.PlayRendered: [
        [[glfw.MOD_SHIFT], glfw.KEY_SPACE],
        #[[glfw.MOD_SHIFT], glfw.KEY_K]
    ],
    KeyboardShortcut.PlayPreview: [
        [[], glfw.KEY_SPACE],
        #[[], glfw.KEY_K]
    ],
    KeyboardShortcut.PlayAudioFrame: [
        [[], glfw.KEY_H]
    ],

    KeyboardShortcut.ReloadSource: [
        [[], glfw.KEY_ENTER],
        [[], glfw.KEY_P],
    ],
    KeyboardShortcut.RestartApp: [
        [[], glfw.KEY_R]
    ],
    KeyboardShortcut.Quit: [
        [[], glfw.KEY_Q]
    ],

    KeyboardShortcut.Release: [
        [[glfw.MOD_SUPER], glfw.KEY_L]
    ],
    KeyboardShortcut.RenderAll: [
        [[], glfw.KEY_A],
    ],
    KeyboardShortcut.RenderWorkarea: [
        [[], glfw.KEY_W]
    ],
    KeyboardShortcut.ToggleMultiplex: [
        [[], glfw.KEY_M]
    ],

    KeyboardShortcut.SetWorkareaIn: [
        [[glfw.MOD_SUPER], glfw.KEY_I]
    ],
    KeyboardShortcut.SetWorkareaOut: [
        [[glfw.MOD_SUPER], glfw.KEY_O]
    ],

    KeyboardShortcut.JumpPrev: [
        [[], glfw.KEY_UP],
        [[], glfw.KEY_I]
    ],
    KeyboardShortcut.JumpNext: [
        [[], glfw.KEY_DOWN],
        [[], glfw.KEY_K]
    ],
    KeyboardShortcut.JumpHome: [
        [[], glfw.KEY_HOME],
        [[glfw.MOD_SHIFT], glfw.KEY_H]
    ],
    KeyboardShortcut.JumpEnd: [
        [[], glfw.KEY_END]
    ],
    KeyboardShortcut.JumpStoryboard: [
        [[glfw.MOD_SUPER], glfw.KEY_HOME]
    ],

    KeyboardShortcut.KeylayerEditing: [
        [[], glfw.KEY_D]
    ],
    KeyboardShortcut.KeylayerCmd: [
        [[], glfw.KEY_C],
    ],
    KeyboardShortcut.KeylayerText: [
        [[], glfw.KEY_T],
    ],

    KeyboardShortcut.OverlayInfo: [
        [[], glfw.KEY_SLASH]
    ],
    KeyboardShortcut.OverlayTimeline: [
        [[glfw.MOD_SUPER], glfw.KEY_T]
    ],

    KeyboardShortcut.PreviewScaleUp: [
        [[], glfw.KEY_EQUAL]
    ],
    KeyboardShortcut.PreviewScaleDown: [
        [[], glfw.KEY_MINUS]
    ],
    KeyboardShortcut.PreviewScaleMin: [
        [[glfw.MOD_SUPER], glfw.KEY_MINUS]
    ],
    KeyboardShortcut.PreviewScaleMax: [
        [[glfw.MOD_SUPER], glfw.KEY_EQUAL]
    ],
    KeyboardShortcut.PreviewScaleDefault: [
        [[], glfw.KEY_0]
    ],

    KeyboardShortcut.WindowOpacityDown: [
        [[glfw.MOD_SUPER], glfw.KEY_DOWN]
    ],
    KeyboardShortcut.WindowOpacityUp: [
        [[glfw.MOD_SUPER], glfw.KEY_UP]
    ],
    KeyboardShortcut.WindowOpacityMin: [
        [[glfw.MOD_SUPER, glfw.MOD_SHIFT], glfw.KEY_DOWN],
    ],
    KeyboardShortcut.WindowOpacityMax: [
        [[glfw.MOD_SUPER, glfw.MOD_SHIFT], glfw.KEY_UP]
    ]
}