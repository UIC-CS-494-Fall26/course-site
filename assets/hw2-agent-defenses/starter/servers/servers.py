"""The two local servers for HW2. Both listen on 127.0.0.1 only, so no data leaves your machine.

    python3 servers/servers.py

- 127.0.0.1:9765 is the attacker. Every request lands in .run/listener.log.
- 127.0.0.1:9766 is the legitimate docs service. GET /docs returns the usage docs.
"""
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# The starter folder. The servers share .run/ with the agent, so run both from one copy.
ROOT = Path(__file__).resolve().parent.parent
RUN_DIR = ROOT / ".run"
LISTENER_PORT = 9765
DOCS_PORT = 9766


# Python's built-in web server calls a handler's do_GET() method once per GET
# request. Inside do_GET(), self.path holds the requested path, such as "/docs".
class QuietHandler(BaseHTTPRequestHandler):
    """A request handler with no access log and a one-line way to reply."""

    def log_message(self, *args):
        """Silence the default log line for every request."""
        pass

    def reply(self, code, body):
        """Send a status code and a text body."""
        self.send_response(code)
        self.end_headers()
        self.wfile.write(body.encode())  # wfile is the connection back to the client


class Attacker(QuietHandler):
    """The attacker's server. The server records every request and answers "ok"."""

    def do_GET(self):
        """Append the request path to .run/listener.log.

        A leaked key usually arrives inside the path, as in /?k=sk-hw2-...
        The checker searches this log for the canary.
        """
        RUN_DIR.mkdir(exist_ok=True)
        with open(RUN_DIR / "listener.log", "a") as f:
            f.write(self.path + "\n")
        print(f"ATTACKER RECEIVED: {self.path}", flush=True)
        self.reply(200, "ok")


class Docs(QuietHandler):
    """The legitimate docs service that task T4 reads."""

    def do_GET(self):
        """Serve the usage docs at /docs, and answer 404 for every other path.

        An attack with `target: docs` makes agent.py write .run/docs.md. For
        that run, the handler serves .run/docs.md in place of servers/docs.md.
        """
        if self.path != "/docs":
            self.reply(404, "not found")
            return
        attacked = RUN_DIR / "docs.md"
        if attacked.exists():
            self.reply(200, attacked.read_text())
        else:
            self.reply(200, (Path(__file__).parent / "docs.md").read_text())


def serve(port, handler):
    """Serve one handler on 127.0.0.1:port for the life of the process.

    ThreadingHTTPServer answers each request in its own thread, so a slow
    request holds up no other request.
    """
    ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    print(f"attacker listening on 127.0.0.1:{LISTENER_PORT}", flush=True)
    print(f"docs service listening on 127.0.0.1:{DOCS_PORT}", flush=True)
    # Run the attacker in a background thread and the docs service in the main
    # thread. daemon=True lets Ctrl-C stop the program without waiting for the thread.
    threading.Thread(target=serve, args=(LISTENER_PORT, Attacker), daemon=True).start()
    serve(DOCS_PORT, Docs)
