from coldtype import *
from coldtype.fx.skia import vector_pixels

# def vector_pixels(rect, scale=0.1, lut=dict()):
#     import PIL.Image
    
#     def _vector_pixels(pen):
#         raster = pen.ch(rasterized(rect, scale=scale))
#         pi = PIL.Image.fromarray(raster, "RGBa")
#         out = P()
#         for x in range(pi.width):
#             for y in range(pi.height):
#                 r, g, b, a = pi.getpixel((x, y))
#                 res = (r, g, b, a)
#                 if any(res):
#                     lookup = (int(r/255*100), int(g/255*100), int(b/255*100), int(a/255*100))
#                     if lookup in lut:
#                         color = lut[lookup]
#                     else:
#                         print(lookup)
#                         color = hsl(random(), 0.6, 0.6)
                    
#                     out.append(P()
#                         .rect(Rect(x, pi.height-y, 1, 1))
#                         .f(color))
        
#         return out.scale(1/scale, point=(0, 0))
    
#     return _vector_pixels

@renderable((1080, 540))
def scratch(r:Rect):
    return (StSt("ABC", Font.JBMono(), 500, wght=1)
        .align(r)
        #.ch(precompose(r, scale=0.05))
        .ch(vector_pixels(r, scale=0.05, lut={
            (0, 50, 100, 100): hsl(0.65),
            (0, 37, 74, 74): hsl(0.55, a=0.5),
            (0, 25, 50, 50): hsl(0.45, a=0.2),
            (0, 12, 25, 25): hsl(0.45, a=0.1),
        }))
        .align(r))
