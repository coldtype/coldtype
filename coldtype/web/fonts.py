from coldtype.text.font import Font

from pathlib import Path
from dataclasses import dataclass
from typing import List
from shutil import copy2

@dataclass
class WebFont():
    font: Font
    woff2: Path
    bold: bool
    italic: bool
    variations: dict

@dataclass
class WebFontFamily():
    name: str
    variable_name: str
    fonts: List[WebFont]


def get_woff2(src_folder, dst_folder, font_file, bold=False, italic=False):
    src = Font.Cacheable(src_folder / font_file)
    
    if Path(src.path).suffix == ".woff2":
        woff2_src = Path(src.path)
    else:
        woff2_src = Path(src.path).with_suffix(".woff2")
    
    woff2_dst = dst_folder / woff2_src.name
    has_been_modded = False

    if woff2_dst.exists():
        src_mtime = Path(src.path).stat().st_mtime
        dst_mtime = woff2_dst.stat().st_mtime
        has_been_modded = dst_mtime < src_mtime
    
    if not woff2_dst.exists() or has_been_modded:
        if woff2_src.exists():
            copy2(woff2_src, woff2_dst)
        else:
            src.subset(woff2_dst)
    
    variations = src.variations()
    for _, vs in variations.items():
        try:
            del vs["axisNameID"]
            del vs["flags"]
        except KeyError:
            pass
        vs["spread"] = vs["maxValue"] - vs["minValue"]
    
    return WebFont(src, woff2_dst, bold, italic, variations)


def woff2_family(src_folder, dst_folder, font_var, font_dict):
    fonts = []
    for k, v in font_dict.items():
        fonts.append(get_woff2(src_folder, dst_folder, v, bold="bold" in k, italic="italic" in k))
    
    _, family = fonts[-1].font.names()
    return WebFontFamily(family.replace(" ", ""), font_var, fonts)
    

def woff2s(src_folder, dst_folder, families_info):
    src_folder = Path(src_folder).expanduser()
    dst_folder = Path(dst_folder).expanduser()
    dst_folder.mkdir(exist_ok=True, parents=True)

    families = []
    for var_name, family in families_info.items():
        families.append(woff2_family(src_folder, dst_folder, var_name, family))
    
    return families


if __name__ == "__main__":
    woff2s("assets/fonts", {
        "display-font": dict(
            regular="OhnoCasualVariable.woff2"),
        "text-font": dict(
            regular="DegularVariable.woff2")})