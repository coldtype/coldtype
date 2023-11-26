import contextlib, glfw, skia
from OpenGL import GL

WIDTH, HEIGHT = 640, 480

path = skia.Path()
path.moveTo(184, 445)
path.lineTo(249, 445)
path.quadTo(278, 445, 298, 438)
path.quadTo(318, 431, 331, 419)
path.quadTo(344, 406, 350, 390)
path.quadTo(356, 373, 356, 354)
path.quadTo(356, 331, 347, 312)
path.quadTo(338, 292, 320, 280) # <- comment out this line and shape will draw correctly with anti-aliasing
path.close()

@contextlib.contextmanager
def glfw_window():
    if not glfw.init():
        raise RuntimeError('glfw.init() failed')
    glfw.window_hint(glfw.STENCIL_BITS, 8)
    window = glfw.create_window(WIDTH, HEIGHT, '', None, None)
    glfw.make_context_current(window)
    yield window
    glfw.terminate()

@contextlib.contextmanager
def skia_surface(window):
    context = skia.GrDirectContext.MakeGL()
    (fb_width, fb_height) = glfw.get_framebuffer_size(window)
    backend_render_target = skia.GrBackendRenderTarget(
        fb_width,
        fb_height,
        0,  # sampleCnt
        0,  # stencilBits
        skia.GrGLFramebufferInfo(0, GL.GL_RGBA8))
    surface = skia.Surface.MakeFromBackendRenderTarget(
        context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
    assert surface is not None
    yield surface
    context.abandonContext()

with glfw_window() as window:
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    with skia_surface(window) as surface:
        with surface as canvas:
            canvas.drawCircle(100, 100, 40, skia.Paint(Color=skia.ColorGREEN, AntiAlias=True))

            paint = skia.Paint(Color=skia.ColorBLUE)
            paint.setStyle(skia.Paint.kStroke_Style)
            paint.setStrokeWidth(2)
            paint.setAntiAlias(True)
            
            canvas.drawPath(path, paint)

        surface.flushAndSubmit()
        glfw.swap_buffers(window)

        while (glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS
            and not glfw.window_should_close(window)):
            glfw.wait_events()