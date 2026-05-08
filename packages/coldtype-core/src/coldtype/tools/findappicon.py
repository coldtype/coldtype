import subprocess, plistlib, shutil

from coldtype import *
from coldtype.raster import *
from coldtype.tool import *

# mac-only

args = parse_inputs(ººinputsºº, dict(
    app=[None, str, "Must provide app name"],
    size=[512, str],
    ))

size = args["size"]
app_name = args["app"]

if size == "@1x":
    size = 512
elif size == "@2x":
    size = 1024
elif size == "@3x":
    size = 1536
elif size == "@4x":
    size = 2048
else:
    size = int(size)


result = subprocess.run(
    ['mdfind', f'kMDItemKind == "Application" && kMDItemDisplayName == "*{app_name}*"'], capture_output=True, text=True)


tmp = Path("/tmp")
paths = [Path(line) for line in result.stdout.strip().split('\n') if line.endswith('.app')]

apps = []
for path in paths:
    plist = path / "Contents" / "Info.plist"
    if plist.exists():
        with open(plist, "rb") as f:
            plist = plistlib.load(f)
        icon = plist.get("CFBundleIconFile") or plist.get("CFBundleIconName")
        icon = path / "Contents/Resources" / icon
        if icon.exists():
            tmp_output = tmp / f"_coldtype_findappicon_{path.stem}_{size}.png"
            subprocess.run(['sips', '-s', 'format', 'png', '-z', str(size), str(size), str(icon), '--out', tmp_output], check=True, capture_output=True)
            apps.append([path, tmp_output])


@animation(Rect(size, size), tl=Timeline(len(apps)))
def icon_viewer(f:Frame):
    return SkiaImage(apps[f.i][1])


def release(_):
    for _, img in apps:
        shutil.copy(img, img.name)