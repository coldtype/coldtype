from coldtype import *
from coldtype.fx.skia import rasterized, image_shader

r = Rect(540)
image = StSt("TYPE", Font.ColdObvi(), 500, wdth=0).align(r).ch(rasterized(r))

@animation(r, tl=Timeline(60, 30), bg=1)
def warper2(f):
    sksl = f"""
    uniform shader image;
    half4 main(float2 coord) {{
      coord.x += sin(coord.y / {f.e("eeio", rng=(40, 10))}) * {f.e("eeio", rng=(60, 0))};
      return image.eval(coord);
    }}"""

    return P().ch(image_shader(f.a.r, image, sksl))