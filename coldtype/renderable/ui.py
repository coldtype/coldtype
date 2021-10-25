from coldtype.geometry.rect import Rect
from coldtype.renderable.renderable import RenderPass
from coldtype.renderable.animation import animation, Frame

class UIState():
    def __init__(self, cursor, cursor_history, frame):
        self.c = cursor
        self.ch = cursor_history
        self.f = frame
        self.i = frame.i
        self.r = frame.a.r


class ui(animation):
    def __init__(self,
        rect=Rect(1080, 1080),
        clip_cursor=True,
        **kwargs
        ):
        
        self.clip_cursor = clip_cursor

        super().__init__(
            rect=rect,
            preview_only=True,
            interactive=True,
            **kwargs)
    
    def passes(self, action, renderer_state, indices=[]):
        c = renderer_state.cursor
        if self.clip_cursor:
            c = c.clip(self.rect)
        
        frames = self.active_frames(action,
            renderer_state, indices)
        
        return [RenderPass(self, action, i,
            [UIState(c, renderer_state.cursor_history, Frame(i, self))]) for i in frames]