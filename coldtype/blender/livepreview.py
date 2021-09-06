# some code that doesn't really work

import bpy
import blf
import bgl

# import skia
# from OpenGL import GL

# context = skia.GrDirectContext.MakeGL()
# backend = skia.GrBackendRenderTarget(1080, 1080, 0, 0,
#     skia.GrGLFramebufferInfo(0, GL.GL_RGBA8))
# surface = skia.Surface.MakeFromBackendRenderTarget(
#     context, backend,
#     skia.kBottomLeft_GrSurfaceOrigin,
#     skia.kRGBA_8888_ColorType,
#     skia.ColorSpace.MakeSRGB())

def get_fac():
    if bpy.context.space_data.proxy_render_size == 'SCENE':
        fac = bpy.context.scene.render.resolution_percentage/100
    else:
        fac = 1    
    return fac

def view_zoom_preview():
    width = bpy.context.region.width
    height = bpy.context.region.height
    rv1 = bpy.context.region.view2d.region_to_view(0,0)
    rv2 = bpy.context.region.view2d.region_to_view(width-1,height-1)
    zoom = (1/(width/(rv2[0]-rv1[0])))/get_fac()
    return zoom

class DrawingClass:
    def __init__(self, msg):
        self.msg = msg
        self.handle = bpy.types.SpaceSequenceEditor.draw_handler_add(
            self.draw_text_callback, (), 'PREVIEW', 'POST_PIXEL')

    def draw_text_callback(self):
        #print(">>>", view_zoom_preview())
        pt = bpy.context.region.view2d.view_to_region(-540,-540,clip=False)
        
#        font_id = 0  # XXX, need to find out how best to get this.
#        blf.position(font_id, pt[0], pt[1], 0)
#        blf.size(font_id, 66, 72)
#        blf.draw(font_id, "%s" % (self.msg))

        #GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        #with surface as context:
        #    context.clear(skia.Color4f(1, 0.3, 0.1, 1))
        #surface.flushAndSubmit()

    def remove_handle(self):
         bpy.types.SpaceSequenceEditor.draw_handler_remove(self.handle, 'PREVIEW')

widgets = {}
def register():
    widgets["Test"] = DrawingClass("Test2")

def unregister():
    for key, dc in widgets.items():
        dc.remove_handle()

if __name__ == "__main__":
    register()