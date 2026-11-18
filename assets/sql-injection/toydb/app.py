"""Toy staff directory with three planted SQL-injection bugs.

    python3 app.py          # serves http://127.0.0.1:8880

Every query below builds SQL by string concatenation, so user input becomes code.
  1. /search?q=   concatenates into a LIKE clause (UNION reads the users table).
  2. /login       concatenates user and pass (' OR '1'='1' -- bypasses the check).
  3. /staff?sort= concatenates a column name into ORDER BY (identifiers cannot be
     parameterized, so the fix is an allowlist, not a placeholder).
"""
import os
import sqlite3
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


def db():
    c = sqlite3.connect(":memory:")
    c.executescript("""
        CREATE TABLE staff (id INTEGER, name TEXT, title TEXT);
        CREATE TABLE users (username TEXT, password TEXT);
        INSERT INTO staff VALUES (1,'Ada Lovelace','Analyst'),
                                 (2,'Alan Turing','Engineer'),
                                 (3,'Grace Hopper','Director');
        INSERT INTO users VALUES ('admin','s3cr3t-hunter2'),('guest','guest');
    """)
    return c


PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Staff Directory</title>
<style>body{{font-family:sans-serif;max-width:40rem;margin:2rem auto}}
td,th{{text-align:left;padding:.2rem .8rem}} input{{padding:.3rem}}</style></head><body>
<h1>Staff Directory</h1>
<form action="/search"><input name="q" placeholder="search name" value="{q}">
<button>Search</button></form>
<p><a href="/staff?sort=name">sort by name</a> &middot;
   <a href="/staff?sort=title">sort by title</a></p>
{body}
</body></html>"""


def table(rows, cols):
    head = "".join(f"<th>{escape(c)}</th>" for c in cols)
    body = "".join("<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in r) + "</tr>"
                   for r in rows)
    return f"<table><tr>{head}</tr>{body}</table>"


class App(BaseHTTPRequestHandler):
    def reply(self, body, code=200, q=""):
        data = PAGE.format(q=escape(q), body=body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        p = {k: v[0] for k, v in parse_qs(u.query).items()}
        con = db()
        try:
            if u.path == "/search":
                q = p.get("q", "")
                sql = "SELECT name, title FROM staff WHERE name LIKE '%" + q + "%'"  # bug 1
                rows = con.execute(sql).fetchall()
                return self.reply(table(rows, ["name", "title"]), q=q)
            if u.path == "/staff":
                sort = p.get("sort", "name")
                sql = "SELECT name, title FROM staff ORDER BY " + sort               # bug 3
                rows = con.execute(sql).fetchall()
                return self.reply(table(rows, ["name", "title"]))
            if u.path in ("/", ""):
                rows = con.execute("SELECT name, title FROM staff").fetchall()
                return self.reply(table(rows, ["name", "title"]))
            return self.reply("<p>not found</p>", 404)
        except sqlite3.Error as e:
            return self.reply(f"<pre>SQL error: {escape(str(e))}</pre>", 500, q=p.get("q", ""))
        finally:
            con.close()

    def do_POST(self):
        if urlparse(self.path).path != "/login":
            return self.reply("<p>not found</p>", 404)
        n = int(self.headers.get("Content-Length", 0))
        p = {k: v[0] for k, v in parse_qs(self.rfile.read(n).decode()).items()}
        con = db()
        try:
            sql = ("SELECT username FROM users WHERE username = '" + p.get("user", "")
                   + "' AND password = '" + p.get("pass", "") + "'")               # bug 2
            row = con.execute(sql).fetchone()
            msg = f"<p>Welcome, {escape(row[0])}</p>" if row else "<p>Login failed</p>"
            return self.reply(msg)
        except sqlite3.Error as e:
            return self.reply(f"<pre>SQL error: {escape(str(e))}</pre>", 500)
        finally:
            con.close()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    print("Staff Directory on http://127.0.0.1:8880")
    HTTPServer((host, 8880), App).serve_forever()
