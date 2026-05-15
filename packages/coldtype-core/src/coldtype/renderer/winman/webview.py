"""
Localhost web server viewer for coldtype.

Replaces the GLFW window with a web page served on localhost. Open the
URL in any browser. Frames are pushed via SSE (signal only); the browser
fetches the actual PNG bytes from /frame. Mouse and keyboard events POST
back to /input.

Usage:
    from coldtype_web_viewer import ColdtypeWebViewer

    viewer = ColdtypeWebViewer(port=8008)
    viewer.start()
    print(viewer.url)   # open in browser

    while running:
        # Drain any pending input events on the main (render) thread
        for ev in viewer.drain_events():
            if ev["type"] == "mouse": handle_mouse(ev)
            elif ev["type"] == "key": handle_key(ev)

        png = render_current_frame_as_png()
        viewer.set_frame(png)

    viewer.stop()

Callbacks are also supported if you'd rather not poll:
    ColdtypeWebViewer(on_mouse=..., on_key=...)
But note callbacks fire on the HTTP server's worker thread.
"""

import json
import queue
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


CANVAS_HTML = r"""<!doctype html>
<html><head><meta charset="utf-8"><title>coldtype</title><style>
  html, body { margin:0; padding:0; height:100%;
    background:#000; overflow:hidden;
    font-family:-apple-system,BlinkMacSystemFont,sans-serif; color:#888;
  }
  #wrap { width:100%; height:100%;
    display:flex; align-items:center; justify-content:center; }
  #frame { max-width:100%; max-height:100%;
    image-rendering:pixelated; user-select:none; -webkit-user-drag:none; }
  #status { position:fixed; bottom:6px; right:10px;
    font-size:11px; opacity:0.5; pointer-events:none; }
</style></head><body>
<div id="wrap"><img id="frame" draggable="false"></div>
<div id="status">connecting…</div>
<script>
const img = document.getElementById("frame");
const status = document.getElementById("status");

function showFrame(v){
  img.src = "/frame?v=" + v;
}

function post(payload){
  fetch("/input", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify(payload),
    keepalive: true,
  }).catch(()=>{}); // ignore network errors; renderer may be paused
}

function mouseEvent(action, e){
  const r = img.getBoundingClientRect();
  const x = e.clientX - r.left;
  const y = e.clientY - r.top;
  const nx = r.width  ? x / r.width  : 0;
  const ny = r.height ? y / r.height : 0;
  post({
    type:"mouse", action,
    x, y, nx, ny,
    button:e.button, buttons:e.buttons,
    shift:e.shiftKey, alt:e.altKey,
    ctrl:e.ctrlKey, meta:e.metaKey,
  });
}

img.addEventListener("mousedown", e=>{ mouseEvent("down", e); e.preventDefault(); });
img.addEventListener("mouseup",   e=>mouseEvent("up", e));
img.addEventListener("mousemove", e=>mouseEvent("move", e));
img.addEventListener("contextmenu", e=>e.preventDefault());

document.addEventListener("keydown", e=>{
  post({ type:"key", action:"down", key:e.key, code:e.code,
         shift:e.shiftKey, alt:e.altKey, ctrl:e.ctrlKey, meta:e.metaKey,
         repeat:e.repeat });
});
document.addEventListener("keyup", e=>{
  post({ type:"key", action:"up", key:e.key, code:e.code,
         shift:e.shiftKey, alt:e.altKey, ctrl:e.ctrlKey, meta:e.metaKey });
});

function connect(){
  const es = new EventSource("/events");
  es.onopen = ()=> status.textContent = "";
  es.onmessage = e => {
    const msg = JSON.parse(e.data);
    console.log(">>>>>>>>>>>>>>", msg);
    if (msg.type === "frame") showFrame(msg.v);
  };
  es.onerror = ()=>{
    status.textContent = "reconnecting…";
    es.close();
    setTimeout(connect, 500);
  };
}
connect();
</script></body></html>
"""


class ColdtypeWebViewer:
    def __init__(self, on_mouse=None, on_key=None,
                 host="127.0.0.1", port=8008, queue_events=True):
        self._host = host
        self._port = port
        self._on_mouse = on_mouse
        self._on_key = on_key
        self._queue_events = queue_events

        self._frame_lock = threading.Lock()
        self._frame_bytes = b""
        self._frame_version = 0

        self._clients_lock = threading.Lock()
        self._clients = []  # list[queue.Queue] — one per SSE connection

        self._event_queue = queue.Queue() if queue_events else None

        self._httpd = None
        self._thread = None

    @property
    def url(self):
        return f"http://{self._host}:{self._port}/"

    # ---------- public API ----------

    def start(self):
        viewer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a, **kw):
                pass  # silence default access log

            def do_GET(self):
                u = urlparse(self.path)
                if u.path in ("/", "/index.html"):
                    self._serve_html()
                elif u.path == "/frame":
                    self._serve_frame()
                elif u.path == "/events":
                    self._serve_events()
                else:
                    self.send_error(404)

            def do_POST(self):
                u = urlparse(self.path)
                if u.path == "/input":
                    self._handle_input()
                else:
                    self.send_error(404)

            # ---- handlers ----

            def _serve_html(self):
                body = CANVAS_HTML.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _serve_frame(self):
                with viewer._frame_lock:
                    data = viewer._frame_bytes
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(data)))
                # Frames are versioned by query string, so no cache needed.
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                try:
                    self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def _serve_events(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.send_header("X-Accel-Buffering", "no")
                self.end_headers()

                q = queue.Queue()
                with viewer._clients_lock:
                    viewer._clients.append(q)
                    # Send the current frame version on connect so a freshly
                    # opened tab gets the latest frame immediately.
                    initial_version = viewer._frame_version

                try:
                    if initial_version > 0:
                        self._send_event({"type": "frame", "v": initial_version})
                    while True:
                        try:
                            msg = q.get(timeout=15)
                        except queue.Empty:
                            try:
                                self.wfile.write(b": ping\n\n")
                                self.wfile.flush()
                            except (BrokenPipeError, ConnectionResetError):
                                break
                            continue
                        if msg is None:
                            break
                        try:
                            self._send_event(msg)
                        except (BrokenPipeError, ConnectionResetError):
                            break
                finally:
                    with viewer._clients_lock:
                        if q in viewer._clients:
                            viewer._clients.remove(q)

            def _send_event(self, msg):
                payload = "data: " + json.dumps(msg) + "\n\n"
                self.wfile.write(payload.encode("utf-8"))
                self.wfile.flush()

            def _handle_input(self):
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length) if length else b""
                try:
                    event = json.loads(raw.decode("utf-8")) if raw else {}
                except Exception:
                    self.send_error(400)
                    return
                viewer._dispatch_input(event)
                self.send_response(204)
                self.end_headers()

        self._httpd = ThreadingHTTPServer((self._host, self._port), Handler)
        self._thread = threading.Thread(
            target=self._httpd.serve_forever,
            name="ColdtypeWebViewer",
            daemon=True,
        )
        self._thread.start()
        print(f"[ColdtypeWebViewer] {self.url}")

    def stop(self):
        if self._httpd is None:
            return
        with self._clients_lock:
            for q in self._clients:
                q.put(None)
            self._clients.clear()
        self._httpd.shutdown()
        self._httpd.server_close()
        self._httpd = None

    def set_frame(self, png_bytes):
        """Update the displayed frame. png_bytes is a bytes-like PNG."""
        data = bytes(png_bytes)
        with self._frame_lock:
            self._frame_bytes = data
            self._frame_version += 1
            v = self._frame_version
        self._broadcast({"type": "frame", "v": v})

    def drain_events(self, max_events=None):
        """Yield queued input events. Call from the render loop on the main
        thread. Returns immediately if no events are pending."""
        if self._event_queue is None:
            return
        n = 0
        while True:
            if max_events is not None and n >= max_events:
                return
            try:
                yield self._event_queue.get_nowait()
            except queue.Empty:
                return
            n += 1

    @property
    def client_count(self):
        """Number of currently connected browser tabs."""
        with self._clients_lock:
            return len(self._clients)

    # ---------- internals ----------

    def _broadcast(self, msg):
        with self._clients_lock:
            clients = list(self._clients)
        for q in clients:
            q.put(msg)

    def _dispatch_input(self, event):
        # Optional callbacks (fire on HTTP worker thread)
        try:
            if event.get("type") == "mouse" and self._on_mouse:
                self._on_mouse(event)
            elif event.get("type") == "key" and self._on_key:
                self._on_key(event)
        except Exception:
            import traceback; traceback.print_exc()
        # Queue for main-thread draining
        if self._event_queue is not None:
            self._event_queue.put(event)


# ---------- demo ----------
if __name__ == "__main__":
    # Generates a moving stripe pattern as a quick smoke test.
    import struct, zlib

    def make_png(w, h, offset):
        # Tiny hand-rolled PNG so the demo has no deps.
        def chunk(tag, data):
            return (struct.pack(">I", len(data)) + tag + data +
                    struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
        raw = bytearray()
        for y in range(h):
            raw.append(0)  # filter
            for x in range(w):
                v = ((x + offset) // 16 + y // 16) & 1
                raw += bytes([255 if v else 30, 80, 200 if v else 60])
        ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
        idat = zlib.compress(bytes(raw))
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", idat) + chunk(b"IEND", b""))

    viewer = ColdtypeWebViewer(port=8008)
    viewer.start()
    print("open", viewer.url)

    offset = 0
    try:
        while True:
            for ev in viewer.drain_events():
                print("event:", ev)
            viewer.set_frame(make_png(400, 300, offset))
            offset += 4
            time.sleep(1/10)
    except KeyboardInterrupt:
        viewer.stop()