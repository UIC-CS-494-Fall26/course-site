"""The legitimate weather service the task needs. Listens on 127.0.0.1:8766 only."""
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Chicago: 12C, windy")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print("weather API listening on 127.0.0.1:8766", flush=True)
    HTTPServer(("127.0.0.1", 8766), Handler).serve_forever()
