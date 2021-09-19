import threading, json

from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer

from coldtype.renderer.winman.passthrough import WinmanPassthrough
from coldtype.renderer.config import ConfigOption, ColdtypeConfig

from coldtype.pens.svgpen import SVGPen
from coldtype.pens.jsonpen import JSONPen

WEBSOCKET_PORT = None

class WebViewerHandler(SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(
            (Path(__file__).parent.parent.parent / "webserver/webviewer.html")
                .read_text()
                .replace("localhost:8007", f"localhost:{WEBSOCKET_PORT}")
                .encode("utf8"))

    def do_HEAD(self):
        self._set_headers()
    
    def log_message(self, format, *args):
        pass

class WinmanWebview(WinmanPassthrough):
    def __init__(self, config:ColdtypeConfig, renderer):
        self.config = config
        self.renderer = renderer

        global WEBSOCKET_PORT
        WEBSOCKET_PORT = self.config.websocket_port

        wv_port = self.config.webviewer_port
        if wv_port != 0:
            print("WEBVIEWER>", f"localhost:{wv_port}")

            def start_server(port):
                httpd = HTTPServer(('', port), WebViewerHandler)
                httpd.serve_forever()

            daemon = threading.Thread(name='daemon_server',
                target=start_server, args=(wv_port,))
            daemon.setDaemon(True)
            daemon.start()
    
    def turn_over(self):
        renders = []
        try:
            title = self.renderer.watchees[0][1].name
        except:
            title = "coldtype"

        for idx, (render, result, rp) in enumerate(self.renderer.previews_waiting):
            if self.renderer.args.format == "canvas": # TODO config?
                renders.append(dict(
                    fmt="canvas",
                    jsonpen=JSONPen.Composite(result, render.rect),
                    rect=[*render.rect],
                    bg=[*render.bg]))
            else:
                renders.append(dict(
                    fmt="svg", svg=SVGPen.Composite(
                        result,
                        render.rect,
                        viewBox=render.viewBox),
                    rect=[*render.rect],
                    bg=[*render.bg]))
    
        if renders:
            for _, client in self.renderer.server.connections.items():
                if hasattr(client, "webviewer") and client.webviewer:
                    client.sendMessage(json.dumps({
                        "renders":renders,
                        "title":title
                    }))
        
        return []
