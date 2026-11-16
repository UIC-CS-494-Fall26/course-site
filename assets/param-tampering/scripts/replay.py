"""Send one form submission with whatever parameters you choose.

    python3 replay.py http://127.0.0.1:8770/order item=mug price=0.01 qty=1

Use this script to confirm a finding: if the server accepts a value the form
would block, you have a tampering bug. Only target localhost.
"""
import sys
import urllib.request
from urllib.parse import urlencode, urlparse

url, pairs = sys.argv[1], sys.argv[2:]
if urlparse(url).hostname not in ("127.0.0.1", "localhost"):
    sys.exit("replay.py only sends requests to localhost targets")
body = urlencode([tuple(p.split("=", 1)) for p in pairs]).encode()
with urllib.request.urlopen(urllib.request.Request(url, data=body), timeout=5) as r:
    print(r.status, r.read().decode())
