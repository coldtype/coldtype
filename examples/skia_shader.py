from coldtype import *
from coldtype.fx.skia import rasterized
from coldtype.renderable.animation import skia_direct_animation, skia

r = Rect(540)
image = StSt("TYPE", Font.ColdObvi(), 500, wdth=0).align(r).ch(rasterized(r))

@skia_direct_animation(r, tl=Timeline(60, 30))
def warper(f, canvas):
    sksl = f"""
    uniform shader image;
    half4 main(float2 coord) {{
      coord.x += sin(coord.y / {f.e("eeio", rng=(40, 20))}) * {f.e("eeio", rng=(60, 0))};
      return image.eval(coord);
    }}"""

    imageShader = image.makeShader(skia.SamplingOptions(skia.FilterMode.kLinear))

    effect = skia.RuntimeEffect.MakeForShader(sksl)

    children = skia.RuntimeEffectChildPtr(imageShader)
    myShader = effect.makeShader(None, skia.SpanRuntimeEffectChildPtr(children, 1))

    canvas.drawColor(skia.ColorWHITE)
    
    p = skia.Paint()
    p.setShader(myShader)
    canvas.drawPaint(p)