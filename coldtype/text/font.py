import os, re, tempfile
from pathlib import Path
from functools import lru_cache
from urllib.request import urlretrieve

from coldtype.osutil import on_linux, on_mac, on_windows

from coldtype.fontgoggles.font import getOpener
from coldtype.fontgoggles.font.baseFont import BaseFont
from coldtype.fontgoggles.font.otfFont import OTFFont

BLACKRENDER_ALL = False

try:
    from blackrenderer.font import BlackRendererFont
    #from blackrenderer.backends.pathCollector import PathCollectorSurface, PathCollectorRecordingPen
    from coldtype.text.colr.brsurface import BRPathCollectorSurface, BRPathCollectorRecordingPen
except ImportError:
    BlackRendererFont = None
    pass



# OS Font paths
try:
    _HOME = Path.home()
except Exception:  # Exceptions thrown by home() are not specified...
    _HOME = Path(os.devnull)  # Just an arbitrary path with no children.
MSFolders = \
    r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
MSFontDirectories = [
    r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts',
    r'SOFTWARE\Microsoft\Windows\CurrentVersion\Fonts']
MSUserFontDirectories = [
    str(_HOME / 'AppData/Local/Microsoft/Windows/Fonts'),
    str(_HOME / 'AppData/Roaming/Microsoft/Windows/Fonts'),
    str(_HOME / 'AppData/Roaming/Adobe/CoreSync/livetype/r'),
]

def list_fonts(directory, extensions):
    """
    Return a list of all fonts matching any of the extensions, found
    recursively under the directory.
    """
    extensions = ["." + ext for ext in extensions]
    return [os.path.join(dirpath, filename)
            # os.walk ignores access errors, unlike Path.glob.
            for dirpath, _, filenames in os.walk(directory)
            for filename in filenames
            if Path(filename).suffix.lower() in extensions]


def win32FontDirectory():
    r"""
    Return the user-specified font directory for Win32.  This is
    looked up from the registry key ::

      \\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders\Fonts

    If the key is not found, ``%WINDIR%\Fonts`` will be returned.
    """
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, MSFolders) as user:
            return winreg.QueryValueEx(user, 'Fonts')[0]
    except OSError:
        return os.path.join(os.environ['WINDIR'], 'Fonts')


def _get_win32_installed_fonts():
    """List the font paths known to the Windows registry."""
    import winreg
    items = set()
    # Search and resolve fonts listed in the registry.
    for domain, base_dirs in [
            (winreg.HKEY_LOCAL_MACHINE, [win32FontDirectory()]),  # System.
            (winreg.HKEY_CURRENT_USER, MSUserFontDirectories),  # User.
    ]:
        for base_dir in base_dirs:
            for reg_path in MSFontDirectories:
                try:
                    with winreg.OpenKey(domain, reg_path) as local:
                        for j in range(winreg.QueryInfoKey(local)[1]):
                            # value may contain the filename of the font or its
                            # absolute path.
                            key, value, tp = winreg.EnumValue(local, j)
                            if not isinstance(value, str):
                                continue
                            try:
                                # If value contains already an absolute path,
                                # then it is not changed further.
                                path = Path(base_dir, value).resolve()
                            except RuntimeError:
                                # Don't fail with invalid entries.
                                continue
                            items.add(path)
                except (OSError, MemoryError):
                    continue
    return items





_prefixes = [
    ["¬", "~/Library/Fonts"],
    ["", "/Library/Fonts"]
]

ALL_FONT_DIRS = []

if on_mac():
    ALL_FONT_DIRS = [
        ".",
        "/System/Library/Fonts",
        "/Library/Fonts",
        "~/Library/Fonts",
    ]

elif on_windows():
    ALL_FONT_DIRS = [
        ".",
        "C:/Windows/Fonts",
    ]

    localappdata = os.environ.get("LOCALAPPDATA")
    if localappdata:
        ALL_FONT_DIRS.append(str(Path(localappdata) / "Microsoft/Windows/Fonts/"))

elif on_linux():
    ALL_FONT_DIRS = ["."]
    # TODO what are the default linux font installation dirs?
    pass

FONT_FIND_DEPTH = 3

class FontNotFoundException(Exception):
    pass

def normalize_font_prefix(path_string):
    for prefix, expansion in _prefixes:
        path_string = path_string.replace(prefix, expansion)
    return Path(path_string).expanduser().resolve()

def normalize_font_path(font, nonexist_ok=False):
    global _prefixes
    literal = normalize_font_prefix(str(font))
    ufo = literal.suffix == ".ufo"
    if nonexist_ok:
        return str(literal)
    if literal.exists() and (not literal.is_dir() or ufo):
        return str(literal)
    else:
        raise FontNotFoundException(literal)

FontCache = {}

class Font():
    # TODO support glyphs?
    def __init__(self, path,
        number=0,
        cacheable=False,
        suffix=None,
        delete_tmp=False
        ):
        tmp = None
        if isinstance(path, str) and path.startswith("http"):
            url = Path(path)
            sfx = url.suffix
            if not sfx:
                sfx = suffix
            with tempfile.NamedTemporaryFile(prefix="coldtype_download_temp", suffix="."+sfx, delete=False) as tmp:
                urlretrieve(path, tmp.name)
                path = tmp.name
                tmp = tmp
        
        self.path = Path(normalize_font_path(path))
        numFonts, opener, getSortInfo = getOpener(self.path)
        self.font:BaseFont = opener(self.path, number)
        self.font.cocoa = False
        self.cacheable = cacheable
        self._loaded = False
        self.load()

        self._colr = self.font.ttFont.get("COLR")
        self._colrv1 = (self._colr is not None
            #and self._colr.version == 1
            and BlackRendererFont is not None)

        if self._colrv1 or BLACKRENDER_ALL:
            self._brFont = BlackRendererFont(self.path, fontNumber=number)
        else:
            self._brFont = None

        self._variations = self.font.ttFont.get("fvar")

        if tmp and delete_tmp:
            os.unlink(tmp.name)
    
    def load(self):
        if self._loaded:
            return self
        else:
            self.font.load(None)
            self._loaded = True
            return self
    
    def variations(self):
        axes = {}
        if self._variations:
            fvar = self._variations
            for axis in fvar.axes:
                axes[axis.axisTag] = (axis.__dict__)
        return axes
    
    def names(self):
        FONT_SPECIFIER_NAME_ID = 4
        FONT_SPECIFIER_FAMILY_ID = 1
        name = ""
        family = ""

        def decode(rec):
            return str(rec)
            # TODO should this be necessary?
            try:
                return rec.string.decode("utf-8")
            except UnicodeDecodeError:
                return rec.string.decode("utf-16-be")

        for record in self.font.ttFont['name'].names:
            if record.nameID == FONT_SPECIFIER_NAME_ID and not name:
                name = decode(record)
            elif record.nameID == FONT_SPECIFIER_FAMILY_ID and not family:
                family = decode(record)
            if name and family:
                break
        return name, family
    
    @staticmethod
    def Cacheable(path, suffix=None, delete_tmp=False, actual_path=None):
        """use actual_path to override a key path (if the actual path is the result of a networked call)"""
        if path not in FontCache:
            FontCache[path] = Font(
                actual_path if actual_path else path,
                cacheable=True,
                suffix=suffix,
                delete_tmp=delete_tmp).load()
        return FontCache[path]
    
    @staticmethod
    def GDrive(id, suffix, delete=True):
        dwnl = f"https://drive.google.com/uc?id={id}&export=download"
        return Font.Cacheable(dwnl, suffix=suffix, delete_tmp=delete)
    
    @staticmethod
    def GoogleFont(font_name, index=0) -> "Font":
        import requests, zipfile, io

        font_name_short = font_name.replace(" ", "")
        font_cache_key = f"GoogleFont_{font_name_short}_{index}"
        if font_cache_key in FontCache:
            return FontCache[font_cache_key]

        url = f"https://fonts.google.com/download?family={font_name}"
        folder = Path(f"_GoogleFonts/{font_name_short}")
        folder.mkdir(exist_ok=True, parents=True)

        r = requests.get(url)
        if not r.ok:
            raise FontNotFoundException("GoogleFont URL did not resolve")
        
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(folder)
        
        font_path = list(folder.glob("*.ttf"))[index]
        return Font.Cacheable(font_cache_key, actual_path=font_path)
    
    def _ListDir(dir, regex, regex_dir, log=False, depth=0):
        if dir.name in [".git", "venv"]:
            return
        
        #print(dir.stem, depth, len(os.listdir(dir)))
        results = []

        for p in dir.iterdir():
            if p.is_dir() and depth < FONT_FIND_DEPTH and p.suffix != ".ufo":
                try:
                    res = Font._ListDir(p, regex, regex_dir, log, depth=depth+1)
                    if res:
                        results.extend(res)
                except PermissionError:
                    pass
            else:
                if regex_dir and not re.search(regex_dir, str(p.parent), re.IGNORECASE):
                    continue
                if re.search(regex, p.name, re.IGNORECASE):
                    if p.suffix in [".otf", ".ttf", ".ttc", ".ufo"]:
                        results.append(p)
        
        return results

    @lru_cache()
    def List(regex, regex_dir=None, log=False, font_dir=None, max_depth=FONT_FIND_DEPTH):
        results = []
        
        font_dirs = ALL_FONT_DIRS
        if font_dir is not None:
            font_dirs = [font_dir]
        
        for dir in font_dirs:
            dir = normalize_font_prefix(dir)
            results.extend(Font._ListDir(Path(dir), regex, regex_dir, log, depth=0))
        return sorted(results, key=lambda p: p.stem)

    @staticmethod
    def Find(regex, regex_dir=None, index=0):
        if isinstance(regex, Font):
            return regex

        if Path(normalize_font_prefix(regex)).expanduser().exists():
            return Font.Cacheable(regex)
        
        found = Font.List(regex, regex_dir)
        try:
            return Font.Cacheable(found[index])
        except Exception as e:
            #print(">", e)
            raise FontNotFoundException(regex)
    
    @staticmethod
    def LibraryList(regex, print_list=False):
        try:
            regex.match("asdf")
        except AttributeError:
            regex = re.compile(f".*{regex}.*", re.IGNORECASE)

        if on_mac():
            import AppKit
            fonts = [x for x in list(AppKit.NSFontManager.sharedFontManager().availableFonts()) if not x.startswith(".")]
            fonts = list(sorted(fonts, key=lambda x: len(x)))
            fonts = [x for x in fonts if re.search(regex, x)]
            if print_list:
                print("---")
                print("Font Matches")
                for f in fonts:
                    print(" >", f)
            return fonts
        elif on_windows():
            import win32gui

            def callback(font, tm, fonttype, names):
                names.append(font.lfFaceName)
                return True

            font_names = []
            hdc = win32gui.GetDC(None)
            win32gui.EnumFontFamilies(hdc, None, callback, font_names)
            print("\n".join(font_names))
            win32gui.ReleaseDC(hdc, None)

            print(">>>", font_names)
        else:
            raise Exception("Library not supported on this OS")
    
    @staticmethod
    def LibraryFind(regex, print_list=False):
        matches = Font.LibraryList(regex, print_list=print_list)
        if len(matches) > 0:
            if on_mac():
                import AppKit, CoreText
                try:
                    font = AppKit.NSFont.fontWithName_size_(matches[0], 100)
                    path = Path(CoreText.CTFontDescriptorCopyAttribute(font.fontDescriptor(), CoreText.kCTFontURLAttribute).path())
                    return Font.Cacheable(path)
                except:
                    print("FAILED SYSTEM LOOKUP", matches[0])
                    raise FontNotFoundException(regex)
    
    def RegisterDir(dir):
        global ALL_FONT_DIRS
        if dir not in ALL_FONT_DIRS:
            ALL_FONT_DIRS.insert(0, dir)
    
    def Normalize(font, fallback=True):
        if isinstance(font, Path):
            font = str(font)
        
        if isinstance(font, str):
            try:
                _font = Font.Find(font)
                _font.load() # necessary?
                return _font
            except FontNotFoundException as e:
                if fallback:
                    #print("font not found:", font)
                    return Font.RecursiveMono()
                else:
                    raise e
        elif isinstance(font, Font):
            return font
        else: # it's a list of fonts
            for f in font:
                try:
                    return Font.Normalize(f, fallback=False)
                except FontNotFoundException:
                    pass
            if fallback:
                return Font.RecursiveMono()
            else:
                raise FontNotFoundException()

    @staticmethod
    def ColdtypeObviously():
        return Font.Cacheable(Path(__file__).parent.parent / "demo/ColdtypeObviously-VF.ttf")
    
    ColdObvi = ColdtypeObviously

    @staticmethod
    def MutatorSans():
        return Font.Cacheable(Path(__file__).parent.parent / "demo/MutatorSans.ttf")
    
    MuSan = MutatorSans
    
    @staticmethod
    def RecursiveMono():
        return Font.Cacheable(Path(__file__).parent.parent / "demo/RecMono-CasualItalic.ttf")
    
    RecMono = RecursiveMono