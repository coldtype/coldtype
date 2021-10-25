from coldtype.geometry.rect import Rect
from coldtype.renderable.renderable import renderable, Action, RenderPass, Overlay
from coldtype.renderable.animation import animation, Frame

class UIState():
    def __init__(self, mouse, frame):
        self.m = mouse
        self.f = frame
        self.i = frame.i
        self.r = frame.a.r


class ui(animation):
    def __init__(self,
        rect=Rect(1080, 1080),
        clip_mouse=True,
        **kwargs
        ):
        
        self.clip_mouse = clip_mouse

        super().__init__(
            rect=rect,
            preview_only=True,
            interactive=True,
            **kwargs)
    
    def passes(self, action, renderer_state, indices=[]):
        m = renderer_state.mouse
        if self.clip_mouse:
            m = m.clip(self.rect)
        
        frames = self.active_frames(action,
            renderer_state, indices)
        
        return [RenderPass(self, action, i,
            [UIState(m, Frame(i, self))]) for i in frames]