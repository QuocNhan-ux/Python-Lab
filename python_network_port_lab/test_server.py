"""Local-only HTTP server so you have a known open port to test."""
from http.server import BaseHTTPRequestHandler, HTTPServer


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = b"Local security lab test server\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8765), DemoHandler)
    print("Local test server at http://127.0.0.1:8765 (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping test server")
    finally:
        server.server_close()
