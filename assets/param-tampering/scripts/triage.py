"""Triage: score each target for parameter-tampering risk.

  bash scripts/fetch_targets.sh          # first, to get the source
  python3 scripts/triage.py --model <name>

For each target the script collects compact evidence (hidden fields, client-only
validation, price/role/id parameters, bulk request binding), sends one digest per
target to the model with the triage prompt, and prints the ranked table. Open each
cited file:line before you trust a score.
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

# One compact signal set. Each pattern names a tampering smell.
SIGNALS = [
    ("hidden field", re.compile(r'type=["\']hidden["\']', re.I)),
    ("disabled/readonly field", re.compile(r'\b(disabled|readonly)\b', re.I)),
    ("client-only check (min/max/pattern)", re.compile(r'\b(min|max|maxlength|pattern)=', re.I)),
    ("price/amount/total param", re.compile(r'\b(price|amount|total|cost)\b', re.I)),
    ("role/admin/owner param", re.compile(r'\b(role|is_admin|admin|owner|user_id)\b', re.I)),
    ("bulk request binding", re.compile(r'(getValues\(\)|request->all\(\)|\$_POST|request\.form|fill\(\$request)', re.I)),
]
CODE_EXT = {".php", ".js", ".html", ".tpl", ".twig", ".blade.php", ".java", ".vue"}


def digest(target_dir, max_hits=3):
    lines = []
    for label, pat in SIGNALS:
        hits = []
        for f in target_dir.rglob("*"):
            if f.is_file() and (f.suffix in CODE_EXT) and "node_modules" not in str(f) and "/vendor/" not in str(f):
                try:
                    for i, ln in enumerate(f.read_text(errors="replace").splitlines(), 1):
                        if pat.search(ln):
                            rel = f.relative_to(target_dir)
                            hits.append(f"{rel}:{i}: {ln.strip()[:120]}")
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

    blocks = []
    for d in sorted(p for p in SRC.iterdir() if p.is_dir()):
        blocks.append(f"### repo: {d.name}\n{digest(d)}")
    user = (PROMPTS / "triage.md").read_text() + "\n\n" + "\n\n".join(blocks)
    system = "You are a careful security analyst. Score only on the evidence shown. Invent no file:line."
    print(ask(a.model, system, user))


if __name__ == "__main__":
    main()
