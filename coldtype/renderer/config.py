from enum import Enum
import argparse, re, platform
from pathlib import Path


def true_false_or_none(x):
    if x in ["0", "false", "False", "n", "no", "N"]:
        return False
    elif x in ["1", "true", "True", "y", "yes", "Y"]:
        return True
    else:
        return None
    

def default_blender_app_path():
    sys = platform.system()
    if sys == "Darwin":
        return Path("/Applications/Blender.app/Contents/MacOS/blender").resolve()
    elif sys == "Windows":
        return Path("C:/Program Files/Blender Foundation/Blender/blender.exe").resolve()
    else:
        return None
        #raise Exception("No default blender app path for this platform, please configure via .coldtype.py file and `BLENDER_APP_PATH=`")


def mod_blender_app_path(bap):
    if isinstance(bap, str):
        bap = Path(bap).expanduser().resolve()
    if bap:
        if bap.suffix == ".app":
            bap = bap / "Contents/MacOS/blender"
    return bap


class ConfigOption(Enum):
    WindowPassthrough = ("window_passthrough", None, "wpass", true_false_or_none)
    WindowTransparent = ("window_transparent", None, "wt", true_false_or_none)
    WindowChromeless = ("window_chromeless", None, "wc",  true_false_or_none)
    WindowBackground = ("window_background", None, "wb", true_false_or_none)
    WindowFloat = ("window_float", None, "wf", true_false_or_none)
    WindowOpacity = ("window_opacity", 1, "wo", lambda x: float(x))
    WindowPin = ("window_pin", "SE", "wp")
    WindowPinInset = ("window_pin_inset", (0, 0), "wpi",
        lambda x: [int(n) for n in x.split(",")])
    WindowContentScale = ("window_content_scale", None, "wcs", lambda x: float(x))
    MonitorName = ("monitor_name", None, "mn")
    EditorCommand = ("editor_command", "code", "ec")
    ManyIncrement = ("many_increment", None, "minc")
    PreviewScale = ("preview_scale", 1, "ps", lambda x: float(x))
    FontDirs = ("font_dirs", [], "fd")
    FunctionFilters = ("function_filters", "", "ff",
        lambda x: [re.compile(f.strip()) for f in x.split(",")])
    Midi = ("midi", {}, None)
    Hotkeys = ("hotkeys", {}, None)
    ThreadCount = ("thread_count", 8, "tc")
    Multiplex = ("multiplex", None, "mp", true_false_or_none)
    DebounceTime = ("debounce_time", 0.25, "dt")
    RefreshDelay = ("refresh_delay", 0.025, "rdly")
    InlineFiles = ("inline_files", [], "in", lambda x: x.split(","))
    FFMPEGCommand = ("ffmpeg_command", "ffmpeg", "ffc")
    BlenderWatch = ("blender_watch", None, "bw", true_false_or_none)
    BlenderAppPath = ("blender_app_path", default_blender_app_path(), "bap",
        lambda x: Path(x).expanduser().resolve(),
        mod_blender_app_path)
    BlenderFile = ("blender_file", None, "bf",
        lambda x: Path(x).expanduser().resolve())
    NoViewer = ("no_viewer", None, "nv", true_false_or_none)
    NoMIDI = ("no_midi", None, "nm", true_false_or_none)
    MIDIInfo = ("midi_info", None, "mi", true_false_or_none)
    NoSound = ("no_sound", None, "ns", true_false_or_none)
    NoViewerErrors = ("no_viewer_errors", None, "nve", true_false_or_none)
    EnableAudio = ("enable_audio", None, "ea", true_false_or_none)
    AddTimeViewers = ("add_time_viewers", None, "tv", true_false_or_none)
    ShowXray = ("show_xray", None, "x", true_false_or_none)
    ShowGrid = ("show_grid", None, "g", true_false_or_none)
    GridSettings = ("grid_settings", [], "gs", lambda x: x.split(","))
    PrintResult = ("print_result", None, "pr", true_false_or_none)
    LoadOnly = ("load_only", None, "lo", true_false_or_none)
    TestDirectoryDelay = ("test_directory_delay", 10, "tdd", lambda x: int(x))
    VersionIndex = ("version_index", 0, "vi", lambda x: int(x))

    @staticmethod
    def Help(e):
        if e == ConfigOption.WindowPassthrough:
            return "Should the window ignore all interaction?"
        elif e == ConfigOption.WindowTransparent:
            return "Should the window have no background?"
        elif e == ConfigOption.WindowChromeless:
            return "Should the window have no chrome?"
        elif e == ConfigOption.WindowBackground:
            return "Should the window open as a background process?"
        elif e == ConfigOption.WindowFloat:
            return "Should the window float above everything?"
        elif e == ConfigOption.WindowOpacity:
            return "A value for the transparency of the window"
        elif e == ConfigOption.WindowPin:
            return "Where should the window show up? Provide a compass direction N/S/E/W/NE/SE/SW/NW/C"
        elif e == ConfigOption.WindowPinInset:
            return "Experimental; offset window pin from edge"
        elif e == ConfigOption.WindowContentScale:
            return "Experimental; override auto-calculated window scale"
        elif e == ConfigOption.MonitorName:
            return "The name of the monitor to open the window in; pass 'list' to list all monitor names"
        elif e == ConfigOption.EditorCommand:
            return "If your text editor provides a command-line invocation, set it here for automated opening"
        elif e == ConfigOption.ManyIncrement:
            return "How many frames should the renderer jump forward when you hit cmd+arrow to move prev/next?"
        elif e == ConfigOption.PreviewScale:
            return "What preview scale should the window open at?"
        elif e == ConfigOption.FontDirs:
            return "What additional directories would you like to search for fonts?"
        elif e == ConfigOption.FunctionFilters:
            return "Do you want to restrict renderable functions to those that match these comma-delimited patterns?"
        elif e == ConfigOption.ThreadCount:
            return "How many threads when multiplexing?"
        elif e == ConfigOption.Multiplex:
            return "Should the renderer run multiple processes (determined by --thread-count)?"
        elif e == ConfigOption.DebounceTime:
            return "How long should the rendering loop wait before acting on a debounced action?"
        elif e == ConfigOption.RefreshDelay:
            return "How long should the renderer delay between rendering frames?"
        elif e == ConfigOption.BlenderWatch:
            return "Enable experimental blender live-coding integration?"
        elif e == ConfigOption.NoViewer:
            return "Should there be no viewer at all?"
        elif e == ConfigOption.NoMIDI:
            return "Should MIDI be disabled?"
        elif e == ConfigOption.MIDIInfo:
            return "Should information about the current MIDI setup and messages be printed while the program runs?"
        elif e == ConfigOption.NoSound:
            return "Turn off all sounds made by the renderer"
        elif e == ConfigOption.NoViewerErrors:
            return "Turn off displaying errors in the viewer"
        elif e == ConfigOption.EnableAudio:
            return "Enable audio playback if audio is defined on an @animation"
        elif e == ConfigOption.AddTimeViewers:
            return "Begin with time-viewers visible?"
        elif e == ConfigOption.ShowXray:
            return "Show the Bezier xray instead of the thing itself?"
        elif e == ConfigOption.ShowGrid:
            return "Add a grid to the output?"
        elif e == ConfigOption.PrintResult:
            return "Print the result"
        

    @staticmethod
    def AddCommandLineArgs(pargs:dict,
        parser:argparse.ArgumentParser
        ):
        for co in ConfigOption:
            if co.value[2]:
                short = co.value[2]
                arg = co.value[0].replace("_", "-")
                type_spec = dict(default=None)
                #if co.value[1] is False:
                #    type_spec = dict(action="store_true", default=False)
                pargs[co.value[0]] = parser.add_argument(f"-{short}", f"--{arg}", help=ConfigOption.Help(co), **type_spec)
    
    @staticmethod
    def ShortToConfigOption(short):
        for co in ConfigOption:
            if short == co.value[2]:
                return co


_set_paths = {}


class ColdtypeConfig():
    def __init__(self,
        config,
        prev_config:"ColdtypeConfig"=None,
        args=None
        ):
        global _set_paths

        self.profile = None
        if args and hasattr(args, "profile") and args.profile:
            self.profile = args.profile
        
        for co in ConfigOption:
            post_mod = None

            if len(co.value) > 4:
                prop, default_value, _, cli_mod, post_mod = co.value
            elif len(co.value) > 3:
                prop, default_value, _, cli_mod = co.value
            else:
                prop, default_value, _ = co.value
                cli_mod = lambda x: x
            
            if prop in _set_paths and prev_config:
                setattr(self, prop, getattr(prev_config, prop))
            else:
                value = config.get(prop.upper(), getattr(prev_config, prop) if prev_config else default_value)
                setattr(self, prop, value)
            
            if self.profile and "PROFILES" in config and self.profile in config["PROFILES"]:
                v = config["PROFILES"][self.profile].get(prop.upper())
                if v:
                    _set_paths[prop] = "PROFILE"
                    setattr(self, prop, v)
            
            if args and hasattr(args, prop):
                value = getattr(args, prop)
                if value is not None:
                    #print("CLI", prop, value)
                    setattr(self, prop, cli_mod(value))
            
            if post_mod:
                setattr(self, prop, post_mod(getattr(self, prop)))
    
    def values(self):
        out = "<ColdtypeConfig:"
        if self.profile:
            out += f"({self.profile})"
        for co in ConfigOption:
            out += f"\n   {co.name}:{getattr(self, co.value[0])}"
        out += "/>"
        return out