from coldtype import *
import dominate.tags as dt

src = Path("test/test_ui_text.txt")

def callback(event):
    if event.get("id") == "cool-textarea":
        src.write_text(event.get("value"))

@renderable(ui_callback=callback)
def render(r):
    ta = dt.textarea(src.read_text(), id="cool-textarea")
    render.preview.send(dt.div(dt.h5("hello"), ta))
    return []