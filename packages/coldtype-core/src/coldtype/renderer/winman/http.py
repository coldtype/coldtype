import os, socket, threading, queue, json

from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from coldtype.renderer.utils import path_hash
from coldtype.renderer.winman.passthrough import WinmanPassthrough

from sourcetypes import jinja_html, css, js


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port_unix(port):
    os.system(f"lsof -i tcp:{port} | awk 'NR!=1 {{print $2}}' | xargs kill")



CANVAS_HTML : jinja_html = r"""<!doctype html>
<html><head><meta charset="utf-8"><title>coldtype</title><style>
    @font-face {
        font-family: 'DefaultFont';
        src: url('default-font.ttf') format('truetype');
    }
    html, body { margin:0; padding:0; background: #fff; font-family: DefaultFont, sans-serif; }
</style></head><body>

<div id="content">Content</div>
<div id="status">connecting…</div>

<script>
const status = document.getElementById("status");

function post(payload) {
  fetch("/input", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify(payload),
    keepalive: true,
  }).catch(()=>{});
}

function mouseEvent(action, e) {
    console.log("mouse event");
}

document.addEventListener("keydown", e=> {
  post({ type:"key", action:"down", key:e.key, code:e.code,
         shift:e.shiftKey, alt:e.altKey, ctrl:e.ctrlKey, meta:e.metaKey,
         repeat:e.repeat });
});

document.addEventListener("keyup", e=> {
  post({ type:"key", action:"up", key:e.key, code:e.code,
         shift:e.shiftKey, alt:e.altKey, ctrl:e.ctrlKey, meta:e.metaKey });
});

function connect(){
  const es = new EventSource("/events");
  es.onopen = ()=> status.textContent = "";
  es.onmessage = e => {
    const msg = JSON.parse(e.data);
    console.log(">>>>>>>>>>>>>>", msg);
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



class WinmanHTTPServer(WinmanPassthrough):
    def __init__(self, config, host="127.0.0.1", port=8008):
        self._host = host
        self._port = port

        self._clients_lock = threading.Lock()
        self._clients = []  # list[queue.Queue] — one per SSE connection

        self._event_queue = queue.Queue()

        self._httpd = None
        self._thread = None

    @property
    def url(self):
        return f"http://{self._host}:{self._port}/"

    def launch(self):
        kill_process_on_port_unix(self._port)
        
        self.start()

        # self.subp = blender_launch_livecode(
        #     self.blender_path,
        #     blender_io.blend_file,
        #     self.command_file,
        #     #reset_factory=self.reset_factory,
        #     additional_args=self.cli_args)
    
    def start(self):
        viewer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a, **kw):
                pass  # silence default access log

            def do_GET(self):
                from coldtype.text.font import Font

                u = urlparse(self.path)
                if u.path in ("/", "/index.html"):
                    self._serve_html()
                elif u.path == "/events":
                    self._serve_events()
                elif u.path == "/default-font.ttf":
                    self._send(Font.JBMono().path.read_bytes(), "font/ttf")
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

                try:
                    self._send_event({"type": "message", "text": "hello"})
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
            
            def _send(self, body, content_type):
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

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
    
    def write_command(self, cmd, arg, kwargs=[]):
        pass

    def did_render(self, count, ditto_last, renders):
        pass
    
    def reload(self, filepath, source_reader):
        print("RELOAD HTTP")
    
    def toggle_playback(self, toggle):
        pass
    
    def frame_offset(self, offset):
        pass

    def terminate(self):
        if self._httpd is None:
            return
        with self._clients_lock:
            for q in self._clients:
                q.put(None)
            self._clients.clear()
        self._httpd.shutdown()
        self._httpd.server_close()
        self._httpd = None
    
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
        print(self, event)
        # # Optional callbacks (fire on HTTP worker thread)
        # try:
        #     if event.get("type") == "mouse" and self._on_mouse:
        #         self._on_mouse(event)
        #     elif event.get("type") == "key" and self._on_key:
        #         self._on_key(event)
        # except Exception:
        #     import traceback; traceback.print_exc()
        # Queue for main-thread draining
        if self._event_queue is not None:
            self._event_queue.put(event)