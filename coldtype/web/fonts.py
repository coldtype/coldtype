from coldtype.text.font import Font

from pathlib import Path
from dataclasses import dataclass
from typing import List
from shutil import copy2


@dataclass
class WebFont():
    font: Font
    woff2: Path
    woff2_relative: Path
    bold: bool
    italic: bool
    variations: dict
    embedded: str = None

    def js_args(self):
        return ", ".join([f"{k}={(v['defaultValue']-v['minValue'])/(v['maxValue']-v['minValue'])}" for k, v in self.variations.items()])
    
    def js_setter(self):
        return ", ".join([f"'{k}' ${{{v['minValue']}+({v['maxValue']}-{v['minValue']})*{k}}}" for k, v in self.variations.items()])


@dataclass
class WebFontFamily():
    name: str
    variable_name: str
    fonts: List[WebFont]
    embed: bool = False

    @property
    def variable_name_js(self):
        return self.variable_name.replace("-", "_")


def get_woff2(root, dst_folder, font_file, bold=False, italic=False, features={}):
    #src = Font.Cacheable(src_folder / font_file)
    src = Font.Find(font_file)
    
    if Path(src.path).suffix == ".woff2":
        woff2_src = Path(src.path)
    else:
        woff2_src = Path(src.path).with_suffix(".woff2")
    
    woff2_dst:Path = dst_folder / woff2_src.name
    has_been_modded = False

    if woff2_dst.exists():
        src_mtime = Path(src.path).stat().st_mtime
        dst_mtime = woff2_dst.stat().st_mtime
        has_been_modded = dst_mtime < src_mtime
    
    if not woff2_dst.exists() or has_been_modded:
        if woff2_src.exists():
            copy2(woff2_src, woff2_dst)
        else:
            src.subset(woff2_dst, features=features)
    
    variations = src.variations()
    for _, vs in variations.items():
        try:
            del vs["axisNameID"]
            del vs["flags"]
        except KeyError:
            pass
        vs["spread"] = vs["maxValue"] - vs["minValue"]
    
    return WebFont(src, woff2_dst, woff2_dst.relative_to(root), bold, italic, variations)
    

def woff2s(dst_folder, families_info, root):
    dst_folder = Path(dst_folder).expanduser()
    dst_folder.mkdir(exist_ok=True, parents=True)

    families = []
    for var_name, family in families_info.items():
        fonts = []
        features = family.get("_features", {})
        embed = "_embed" in family
        for style_name, font in family.items():
            if not style_name.startswith("_"):
                fonts.append(get_woff2(root, dst_folder, font,
                    bold="bold" in style_name,
                    italic="italic" in style_name,
                    features=features))
        _, family = fonts[-1].font.names()
        families.append(WebFontFamily(family.replace(" ", ""), var_name, fonts, embed=embed))
    
    return families


if __name__ == "__main__":
    woff2s("assets/fonts", {
        "display-font": dict(
            regular="OhnoCasualVariable.woff2"),
        "text-font": dict(
            regular="DegularVariable.woff2")})