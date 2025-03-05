import os, re, tempfile, sys
from pathlib import Path
from functools import lru_cache
from urllib.request import urlretrieve

from coldtype.osutil import on_linux, on_mac, on_windows, run_with_check

from fontgoggles.misc.platform import setUseCocoa
setUseCocoa(False)

import fontgoggles.misc.hbShape as hbShape
try:
    hbShape.CLUSTER_LEVEL = hbShape.hb.BufferClusterLevel.DEFAULT
except:
    print("! could not set hbShape.CLUSTER_LEVEL")
    pass

from fontgoggles.font import getOpener
from fontgoggles.font.baseFont import BaseFont

BLACKRENDER_ALL = False

try:
    from blackrenderer.font import BlackRendererFont
    #from blackrenderer.backends.pathCollector import PathCollectorSurface, PathCollectorRecordingPen
    from coldtype.text.colr.brsurface import BRPathCollectorSurface, BRPathCollectorRecordingPen
except ImportError:
    BlackRendererFont = None
    pass

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
FontmakeCache = {}

class Font():
    # TODO support glyphs?
    def __init__(self, path,
        number=0,
        cacheable=False,
        suffix=None,
        delete_tmp=False,
        black=False,
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

        if self._colrv1 or BLACKRENDER_ALL or black:
            self._brFont = BlackRendererFont(self.path, fontNumber=number)
        else:
            self._brFont = None

        self._variations = self.font.ttFont.get("fvar")
        self._instances = None

        if tmp and delete_tmp:
            os.unlink(tmp.name)
    
    def load(self):
        if self._loaded:
            return self
        else:
            from coldtype.helpers import run_coroutine_sync
            run_coroutine_sync(self.font.load(sys.stderr.write))
            self._loaded = True
            return self
    
    def variations(self):
        axes = {}
        if self._variations:
            fvar = self._variations
            for axis in fvar.axes:
                axes[axis.axisTag] = (axis.__dict__)
        return axes
    
    def features(self):
        return {*self.font.featuresGPOS, *self.font.featuresGSUB}
    
    def instances(self, scaled=True, search:re.Pattern=None):
        if self._variations is None:
            return None
        
        if self._instances is None:
            self._instances = {}
            for x in self._variations.instances:
                name_id = x.subfamilyNameID
                name_record = self.font.ttFont["name"].getDebugName(name_id)
                self._instances[name_record] = x.coordinates
        
        if scaled:
            axes = self.variations()
            def scale(cs):
                out = {}
                for k, v in cs.items():
                    axis = axes[k]
                    out[k] = (v - axis["minValue"]) / (axis["maxValue"] - axis["minValue"])
                return out
            return {k:scale(v) for k, v in self._instances.items()}
        
        if search is not None:
            keys = self._instances.keys()
            matches = [key for key in keys if re.search(search, key, re.IGNORECASE)]
            if len(matches) > 0:
                return self._instances[matches[0]]
            else:
                print(f"No instance keys matching: {search} :for {self.path.stem}")
                return None

        return self._instances
    
    def names(self):
        """
        returns name, family
        """
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
    
    def subset(self, output_path, *args, unicodes="U+0000-00FF U+2B22 U+201C U+201D U+201D", features={}):
        _args = [
            "pyftsubset", str(self.path),
            f"--output-file={str(output_path)}",
            f"--unicodes={unicodes}",
            "--ignore-missing-unicodes",
            "--ignore-missing-glyphs",
            "--notdef-outline",
            "--notdef-glyph",
        ]
        
        add_features = []
        subtract_features = []

        for k, v in features.items():
            if v:
                add_features.append(k)
            else:
                subtract_features.append(k)
        
        print(add_features, subtract_features)

        if len(add_features) > 0:
            _args.append("--layout-features+="+",".join(add_features))
        if len(subtract_features) > 0:
            _args.append("--layout-features-="+",".join(subtract_features))

        _args.extend(args)
        print(">>", _args, "<<")
        run_with_check(_args)
        return Font(str(output_path))
    
    @staticmethod
    def Cacheable(path, suffix=None, delete_tmp=False, actual_path=None, number=0):
        """use actual_path to override a key path (if the actual path is the result of a networked call)"""
        if number > 0:
            if not actual_path:
                actual_path = path
            path = f"{path}_#{number}"
        
        if path not in FontCache:
            FontCache[path] = Font(
                actual_path if actual_path else path,
                cacheable=True,
                suffix=suffix,
                delete_tmp=delete_tmp,
                number=number).load()
        return FontCache[path]
    
    @staticmethod
    def GDrive(id, suffix, delete=True):
        dwnl = f"https://drive.google.com/uc?id={id}&export=download"
        return Font.Cacheable(dwnl, suffix=suffix, delete_tmp=delete)
    
    @staticmethod
    def UnzipURL(url, font_name, path, index=0) -> "Font":
        import requests, zipfile, io

        stem = Path(url).stem
        font_name_short = font_name.replace(" ", "")
        font_cache_key = f"DownloadedFont_{font_name_short}_{index}"
        
        if font_cache_key in FontCache:
            return FontCache[font_cache_key]

        folder = Path(f"_DownloadedFonts")
        folder.mkdir(exist_ok=True, parents=True)

        r = requests.get(url)
        if not r.ok:
            raise FontNotFoundException("URL did not resolve")
        
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(folder)

        font_path = folder / stem / path / font_name
        return Font.Cacheable(font_cache_key, actual_path=font_path)
    
    # Google broke this
    # @staticmethod
    # def GoogleFont(font_name, index=0) -> "Font":
    #     import requests, zipfile, io

    #     font_name_short = font_name.replace(" ", "")
    #     font_cache_key = f"GoogleFont_{font_name_short}_{index}"
    #     if font_cache_key in FontCache:
    #         return FontCache[font_cache_key]

    #     url = f"https://fonts.google.com/download?family={font_name}"
    #     folder = Path(f"_GoogleFonts/{font_name_short}")
    #     folder.mkdir(exist_ok=True, parents=True)

    #     r = requests.get(url)
    #     if not r.ok:
    #         raise FontNotFoundException("GoogleFont URL did not resolve")
        
    #     z = zipfile.ZipFile(io.BytesIO(r.content))
    #     z.extractall(folder)
        
    #     font_path = list(folder.glob("*.ttf"))[index]
    #     return Font.Cacheable(font_cache_key, actual_path=font_path)
    
    def Download(url) -> "Font":
        import requests

        font_name = Path(url).name
        
        font_cache_key = f"Download_{font_name}"
        if font_cache_key in FontCache:
            return FontCache[font_cache_key]

        folder = Path(f"_DownloadedFonts")
        folder.mkdir(exist_ok=True, parents=True)
        font_path = folder / font_name

        r = requests.get(url)
        if not r.ok:
            raise FontNotFoundException("URL did not resolve")
        
        font_path.write_bytes(r.content)
        return Font.Cacheable(font_cache_key, actual_path=font_path)
    
    def _ListDir(dir, regex, regex_dir, log=False, depth=0):
        if dir.name in [".git", "venv"]:
            return
        
        #print(dir.stem, depth, len(os.listdir(dir)))
        results = []

        try:
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
                        if p.suffix in [".otf", ".ttf", ".ttc", ".ufo", ".woff", ".woff2"]:
                            results.append(p)
        except FileNotFoundError:
            pass
        
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
    def Find(regex, regex_dir=None, index=0, font_dir=None, number=0):
        if isinstance(regex, Font):
            return regex

        if Path(normalize_font_prefix(regex)).expanduser().exists():
            return Font.Cacheable(regex, number=number)
        
        found = Font.List(regex, regex_dir, font_dir=font_dir)
        try:
            return Font.Cacheable(found[index], number=number)
        except Exception as e:
            #print(">", e)
            raise FontNotFoundException(regex)
    
    @staticmethod
    def LibraryList(regex, print_list=False):
        """pass a compiled re (i.e. re.compile to _not_ ignore case)"""
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

    @staticmethod
    def Fontmake(source, verbose=False, keep_overlaps=False, cli_args=[]):
        import tempfile
        from subprocess import run

        path = Path(source).expanduser()
        if not path.exists():
            raise FontNotFoundException(path)

        mtime = path.stat().st_mtime

        if path.suffix == ".designspace":
            from fontTools.designspaceLib import DesignSpaceDocument
            ds = DesignSpaceDocument.fromfile(path)
            for source in ds.sources:
                mtime = max(Path(source.path).stat().st_mtime, mtime)

        if path in FontmakeCache:
            _mtime, _font = FontmakeCache[path]
            if _mtime == mtime:
                return _font

        print(f"fontmake compiling font {path.name}")

        with tempfile.NamedTemporaryFile(prefix="coldtype_fontmake_", suffix=".ttf", delete=False) as tmp:
            args = ["fontmake", path, "--output-path", tmp.name]
            
            if path.suffix == ".designspace":
                args.extend(["-o", "variable"])
            
            if keep_overlaps:
                args.append("--keep-overlaps")
            
            args.extend(cli_args)
            output = run(args, capture_output=not verbose, check=True)
        
        print(f"/fontmake compiled font {path.name}")
        print(tmp.name)

        font = Font(tmp.name)
        FontmakeCache[path] = [mtime, font] # TODO creation args should also go in cache
        os.unlink(tmp.name)

        return font
    
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
    
    def copy_to(self, path:Path):
        from shutil import copy2
        copy2(self.path, Path(path).expanduser().absolute())
        return self

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

    @staticmethod
    def JetBrainsMono():
        return Font.Cacheable(Path(__file__).parent.parent / "demo/JetBrainsMono.ttf")
    
    JBMono = JetBrainsMono