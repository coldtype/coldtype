from coldtype.geometry.rect import Rect
from coldtype.renderable.renderable import RenderPass, Overlay
from coldtype.renderable.animation import animation, Frame

class UIState():
    def __init__(self,
        cursor,
        cursor_history,
        cursor_recording,
        midi,
        frame
        ):
        self.c = cursor
        self.ch = cursor_history
        self.cr = cursor_recording
        self.f = frame
        self.i = frame.i
        self.r = frame.a.r
        self.midi = midi


class ui(animation):
    def __init__(self,
        rect=Rect(1080, 1080),
        clip_cursor=True,
        cursor_recording={},
        **kwargs
        ):
        
        self.clip_cursor = clip_cursor
        self.cursor_recording = cursor_recording

        super().__init__(
            rect=rect,
            preview_only=True,
            interactable=True,
            **kwargs)
    
    def passes(self, action, renderer_state, indices=[]):
        c = renderer_state.cursor
        
        if self.clip_cursor:
            c = c.clip(self.rect)
        
        frames = self.active_frames(
            action,
            renderer_state,
            indices)
        
        if Overlay.Recording in renderer_state.overlays:
            if len(frames) > 0:
                self.cursor_recording[frames[0]] = c
        
        return [RenderPass(self, action, i,
            [UIState(c,
                renderer_state.cursor_history,
                self.cursor_recording,
                renderer_state.midi,
                Frame(i, self))]) for i in frames]