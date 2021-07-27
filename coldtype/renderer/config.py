from enum import Enum
import argparse


class ConfigOption(Enum):
    WindowPassthrough = ("window_passthrough", False, "wpass")
    WindowTransparent = ("window_transparent", False, "wt")
    WindowBackground = ("window_background", False, "wb")
    WindowFloat = ("window_float", False, "wf")
    WindowOpacity = ("window_opacity", 1, "wo")
    WindowPin = ("window_pin", "NE", "wp")
    WindowPinInset = ("window_pin_inset", (0, 0), "wpi",
        lambda x: [int(n) for n in x.split(",")])
    WindowContentScale = ("window_content_scale", None, "wcs")
    EditorCommand = ("editor_command", None, "ec")
    ManyIncrement = ("many_increment", None, "minc")
    PreviewScale = ("preview_scale", 1, "ps")
    FontDirs = ("font_dirs", [], "fd")
    Midi = ("midi", {}, None)
    Hotkeys = ("hotkeys", {}, None)

    @staticmethod
    def Help(e):
        if e == ConfigOption.WindowPassthrough:
            return "Should the window ignore all interaction?"
        elif e == ConfigOption.WindowTransparent:
            return "Should the window have no background?"
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
        elif e == ConfigOption.EditorCommand:
            return "If your text editor provides a command-line invocation, set it here for automated opening"
        elif e == ConfigOption.ManyIncrement:
            return "How many frames should the renderer jump forward when you hit cmd+arrow to move prev/next?"
        elif e == ConfigOption.PreviewScale:
            return "What preview scale should the window open at?"
        elif e == ConfigOption.FontDirs:
            return "What additional directories would you like to search for fonts?"

    @staticmethod
    def AddCommandLineArgs(pargs:dict,
        parser:argparse.ArgumentParser
        ):
        for co in ConfigOption:
            if co.value[2]:
                short = co.value[2]
                arg = co.value[0].replace("_", "-")
                type_spec = dict(default=None)
                if co.value[1] is False:
                    type_spec = dict(action="store_true", default=False)
                pargs[co.value[0]] = parser.add_argument(f"-{short}", f"--{arg}", help=ConfigOption.Help(co), **type_spec)


class ColdtypeConfig():
    def __init__(self,
        config,
        prev_config:"ColdtypeConfig"=None,
        args=None
        ):
        self.profile = None
        if args and hasattr(args, "profile") and args.profile:
            self.profile = args.profile
        
        for co in ConfigOption:
            if len(co.value) > 3:
                prop, default_value, _, cli_mod = co.value
            else:
                prop, default_value, _ = co.value
                cli_mod = lambda x: x
            #print(co.name, prop, default_value)
            setattr(self,
                prop,
                config.get(prop.upper(),
                    getattr(prev_config, prop) if prev_config else default_value))
            
            if self.profile and "PROFILES" in config and self.profile in config["PROFILES"]:
                v = config["PROFILES"][self.profile].get(prop.upper())
                if v:
                    setattr(self, prop, v)
            
            if args and hasattr(args, prop) and getattr(args, prop):
                setattr(self, prop, cli_mod(getattr(args, prop)))
        
        self.midi = config.get("MIDI")
        self.hotkeys = config.get("HOTKEYS")
    
    def values(self):
        out = "<ColdtypeConfig:"
        if self.profile:
            out += f"({self.profile})"
        for co in ConfigOption:
            out += f"\n   {co.name}:{getattr(self, co.value[0])}"
        out += "/>"
        return out