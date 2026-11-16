"""Toy shop with three planted parameter-tampering bugs.

    python3 shop.py          # serves http://127.0.0.1:8770

The browser enforces every rule below. The server enforces none of them.
  1. price is a hidden field, and the server charges whatever price arrives.
  2. qty has max=5 in HTML and a JS check, and the server accepts any integer.
  3. role is a disabled field, and the server honors a role sent by the client.
"""
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

CATALOG = {"mug": 40.00, "hoodie": 65.00}

FORM = """<!doctype html><html><head><meta charset="utf-8"><title>Toy Shop</title>
<style>body{font-family:sans-serif;max-width:32rem;margin:2rem auto}
label{display:block;margin:.6rem 0}</style></head><body>
<h1>Toy Shop</h1>
<form method="post" action="/order" onsubmit="return check()">
  <label>Item
    <select name="item" onchange="price.value = {mug:'40.00',hoodie:'65.00'}[this.value]">
      <option value="mug">UIC mug ($40.00)</option>
      <option value="hoodie">UIC hoodie ($65.00)</option>
    </select></label>
  <input type="hidden" name="price" id="price" value="40.00">
  <label>Quantity (max 5)
    <input type="number" name="qty" id="qty" value="1" min="1" max="5" required></label>
  <label>Account type
    <input name="role" value="customer" disabled></label>
  <button>Place order</button>
</form>
<script>
function check() {
  const q = Number(document.getElementById('qty').value);
  if (q < 1 || q > 5) { alert('Quantity must be 1 to 5'); return false; }
  return true;
}
</script></body></html>"""


class Shop(BaseHTTPRequestHandler):
    def send(self, body, code=200):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.send(FORM)

    def do_POST(self):
        if self.path != "/order":
            return self.send("not found", 404)
        n = int(self.headers.get("Content-Length", 0))
        p = {k: v[0] for k, v in parse_qs(self.rfile.read(n).decode()).items()}
        item = p.get("item", "mug")
        price = float(p.get("price", CATALOG.get(item, 0)))  # bug 1: trusts the client
        qty = int(p.get("qty", 1))                            # bug 2: no 1..5 check
        role = p.get("role", "customer")                      # bug 3: client picks role
        total = price * qty
        discount = 0.5 if role == "staff" else 0.0
        total *= 1 - discount
        print(f"ORDER item={item} price={price:.2f} qty={qty} role={role} total={total:.2f}")
        self.send(f"<h1>Order placed</h1><p>{qty} x {escape(item)} at ${price:.2f}"
                  f" ({escape(role)})</p><p><b>Charged: ${total:.2f}</b></p>")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    import os
    # Default to localhost for a direct run. In Docker, set HOST=0.0.0.0 and keep
    # the container localhost-only through the port mapping 127.0.0.1:8770:8770.
    host = os.environ.get("HOST", "127.0.0.1")
    print("Toy Shop on http://127.0.0.1:8770")
    HTTPServer((host, 8770), Shop).serve_forever()
