import re

try:
    from measurement.measures import Distance
except ImportError:
    pass

def complex_imperial_to_metric(imperial):
    ft = imperial.real
    inches = imperial.imag
    return Distance(ft=ft).m + Distance(inches=inches).m

def imperial(x):
    return str(complex_imperial_to_metric(eval(x.group(0))))

def imperial_macro(path, src):
    print("DOING THE SRC MACRO")
    return re.sub(r"(?<!\")([0-9]{1,}\+)?[0-9]{1,}\.?[0-9]{0,}j", imperial, src)
    
SRC_MACROS = {
   r".*src_macro\.py": imperial_macro
}

FONT_DIRS = [
    "~/Type/fonts/fonts",
]

#FFMPEG_COMMAND = "/Applications/DrawBot.app/Contents/Resources/ffmpeg"