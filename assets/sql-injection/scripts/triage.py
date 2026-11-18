"""Triage: score each target for SQL-injection risk.

  bash scripts/fetch_targets.sh          # first, to get the source
  python3 scripts/triage.py --model <name>

For each target the script collects compact evidence (concatenated queries, request data
near a query, $wpdb calls without prepare, dynamic ORDER BY), sends one digest per target
to the model with the triage prompt, and prints the ranked table. Open each cited
file:line before you trust a score.
"""
import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _llm import ask  # noqa: E402

ROOT = pathlib.Path(__file__).parent.parent
SRC = ROOT / "targets" / "src"
PROMPTS = ROOT / "prompts"

SIGNALS = [
    ("concatenated query", re.compile(r'(SELECT|INSERT|UPDATE|DELETE).{0,40}["\']\s*\.\s*\$|\$\{?\w+\}?\s*\.\s*["\']|f["\'].*\{.*\}.*(FROM|WHERE)', re.I)),
    ("request data in scope", re.compile(r'\$_(GET|POST|COOKIE|REQUEST|SERVER)\b|request\.(args|form|cookies|GET|POST)', re.I)),
    ("wpdb without prepare", re.compile(r'\$wpdb->(query|get_results|get_var|get_row)\s*\(', re.I)),
    ("dynamic ORDER BY / column", re.compile(r'ORDER\s+BY\s*["\']?\s*\.|ORDER\s+BY\s*\$|\border\s*=\s*\$_', re.I)),
    ("escape or blocklist", re.compile(r'(str_replace|addslashes|preg_replace).{0,40}(select|union|--|\')|real_escape', re.I)),
]
CODE_EXT = {".php", ".py", ".js", ".inc", ".module", ".twig"}


def digest(target_dir, max_hits=3):
    lines = []
    for label, pat in SIGNALS:
        hits = []
        for f in target_dir.rglob("*"):
            if f.is_file() and f.suffix in CODE_EXT and "/vendor/" not in str(f) and "node_modules" not in str(f):
                try:
                    for i, ln in enumerate(f.read_text(errors="replace").splitlines(), 1):
                        if pat.search(ln):
                            hits.append(f"{f.relative_to(target_dir)}:{i}: {ln.strip()[:120]}")
                            if len(hits) >= max_hits:
                                break
                except (OSError, UnicodeError):
                    pass
            if len(hits) >= max_hits:
                break
        lines.append(f"- {label}: " + ("; ".join(hits) if hits else "none found"))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    a = ap.parse_args()
    if not SRC.exists():
        sys.exit("No source yet. Run: bash scripts/fetch_targets.sh")
    blocks = [f"### repo: {d.name}\n{digest(d)}" for d in sorted(p for p in SRC.iterdir() if p.is_dir())]
    user = (PROMPTS / "triage.md").read_text() + "\n\n" + "\n\n".join(blocks)
    system = "You are a careful security analyst. Score only on the evidence shown. Invent no file:line."
    print(ask(a.model, system, user))


if __name__ == "__main__":
    main()
