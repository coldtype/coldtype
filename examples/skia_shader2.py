from coldtype import *
from coldtype.fx.skia import rasterized, image_shader

r = Rect(540)
image = StSt("TYPE", Font.ColdObvi(), 500, wdth=0).align(r).ch(rasterized(r))

@animation(r, tl=Timeline(60, 30), bg=1)
def warper2(f):
    sksl = f"""
float hash(float2 p) {{
    return fract(sin(dot(p, float2(127.1, 311.7))) * 43758.5453123);
}}

float noise(float2 p) {{
    float2 i = floor(p);
    float2 f = fract(p);

    float a = hash(i);
    float b = hash(i + float2(1.0, 0.0));
    float c = hash(i + float2(0.0, 1.0));
    float d = hash(i + float2(1.0, 1.0));

    float2 u = f * f * (3.0 - 2.0 * f);

    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}}

float perlinNoise(float2 p, float persistence) {{
    float total = 0.0;
    float amplitude = 1.0;
    float frequency = 1.0;
    float maxValue = 0.0;

    for (int i = 0; i < 4; ++i) {{
        total += noise(p * frequency) * amplitude;
        maxValue += amplitude;
        amplitude *= persistence;
        frequency *= 2.0;
    }}

    return total / maxValue;
}}

// Main shader program
uniform shader image;
uniform float time;        // Time for animation
//uniform float2 resolution;   // Resolution of the texture
//uniform float strength;    // Strength of displacement

float2 resolution = float2(1080, 1080);
float strength = 1.0;

half4 main(float2 coord) {{
    float2 uv = coord / resolution;

    // Generate Perlin noise
    float noiseValueX = perlinNoise(uv + float2(time, 0.0), 0.5);
    float noiseValueY = perlinNoise(uv + float2(0.0, time), 0.5);

    // Displace UVs
    float2 displacement = float2(noiseValueX, noiseValueY) * strength;
    float2 displacedUV = uv + displacement;

    // Sample the texture
    return image.eval(displacedUV * resolution);
}}"""

    return P().ch(image_shader(f.a.r, image, sksl))