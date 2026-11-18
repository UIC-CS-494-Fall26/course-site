"""Confirm a SQL-injection finding with a safe, read-only probe. Localhost only.

  # error test: send a lone quote and look for a SQL error signature
  python3 probe.py error "http://127.0.0.1:8880/search?q=QINJECT"

  # boolean test: compare a TRUE payload against a FALSE payload of equal length
  python3 probe.py bool "http://127.0.0.1:8880/search?q=QINJECT"

Put the literal QINJECT where the payload goes. The script substitutes only safe,
non-destructive payloads: a lone quote for the error test, and a comment-terminated
`AND '1'='1'` vs `AND '1'='2'` pair for the boolean test. It never sends stacked
queries, UNION writes, or anything that changes data. The default payloads suit a
string context such as LIKE; adjust them in this file for a numeric or other context.
"""
import sys
import urllib.parse
import urllib.request
from urllib.error import HTTPError

MARK = "QINJECT"
TRUE_P = "%' AND '1'='1' -- "     # closes the string, adds a tautology, comments the rest
FALSE_P = "%' AND '1'='2' -- "    # same length, always false
ERR_P = "'"                       # a lone quote breaks an unparameterized string
ERR_SIGNS = ("sql error", "sqlite", "syntax error", "unrecognized token",
             "you have an error in your sql", "mysqli", "mysql_", "pg_query",
             "sqlstate", "quoted string not properly terminated")


def fetch(url):
    if urlparse_host(url) not in ("127.0.0.1", "localhost"):
        sys.exit("probe.py only sends requests to localhost targets")
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return r.status, r.read().decode(errors="replace")
    except HTTPError as e:                      # a SQL error often surfaces as a 500
        return e.code, e.read().decode(errors="replace")


def urlparse_host(url):
    return urllib.parse.urlparse(url).hostname


def put(template, payload):
    return template.replace(MARK, urllib.parse.quote(payload))


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("bool", "error"):
        sys.exit(__doc__)
    mode, template = sys.argv[1], sys.argv[2]
    if MARK not in template:
        sys.exit(f"put {MARK} in the URL where the payload goes")
    if mode == "error":
        code, body = fetch(put(template, ERR_P))
        hit = any(s in body.lower() for s in ERR_SIGNS)
        print(f"error probe: HTTP {code}; SQL error signature {'FOUND' if hit else 'not found'}")
        print("=> likely injectable" if hit else "=> no error signal")
        return
    t_code, t_body = fetch(put(template, TRUE_P))
    f_code, f_body = fetch(put(template, FALSE_P))
    # The payloads are the same length, so the reflected echo adds equal bytes;
    # a length difference then comes from the rows the query returned.
    print(f"TRUE  payload: HTTP {t_code}, {len(t_body)} bytes")
    print(f"FALSE payload: HTTP {f_code}, {len(f_body)} bytes")
    print("=> likely injectable: TRUE and FALSE differ" if len(t_body) != len(f_body)
          else "=> no boolean difference")


if __name__ == "__main__":
    main()
