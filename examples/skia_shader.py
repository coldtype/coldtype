from coldtype import *
from coldtype.renderable.animation import skia_direct_animation, skia

image = skia.Image.open("examples/renders/displace_map_text.png")

@skia_direct_animation(540, tl=Timeline(60, 30))
def warper(f, canvas):
    sksl = f"""
    uniform shader image;
    half4 main(float2 coord) {{
      coord.x += sin(coord.y / {f.e("eeio", rng=(20, 40))}) * {f.e("eeio", rng=(0, 60))};
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