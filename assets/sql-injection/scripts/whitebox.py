"""White-box sink-trace: find sinks, trace sources, check the path.

  python3 scripts/whitebox.py --model <name> \
      --file targets/src/<app>/path/to/handler.php \
      --file targets/src/<app>/path/to/helper.php

The script runs the three lab prompts in order and prints each table. Pass every file on
the path from the request to the query. Read each row against the code, then confirm an
injectable row with probe.py.
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _llm import ask  # noqa: E402

PROMPTS = pathlib.Path(__file__).parent.parent / "prompts"


def load(path):
    return f"FILE: {path}\n\n" + pathlib.Path(path).read_text(errors="replace")


def section(t):
    print("\n" + "=" * 70 + f"\n{t}\n" + "=" * 70)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--file", action="append", required=True, help="a file on the request-to-query path (repeatable)")
    a = ap.parse_args()
    code = "\n\n".join(load(f) for f in a.file)
    system = "You are a careful security analyst. Cite file:line for every row. Invent nothing."

    sinks = ask(a.model, system, load_prompt("find-sinks.md") + "\n\n" + code)
    section("Step 1: sinks"); print(sinks)
    sources = ask(a.model, system, load_prompt("trace-source.md") + f"\n\nSinks:\n{sinks}\n\nCode:\n{code}")
    section("Step 2: sources"); print(sources)
    checked = ask(a.model, system, load_prompt("check-parameterization.md") + f"\n\nSinks and sources:\n{sources}\n\nCode:\n{code}")
    section("Step 3: injectable paths (confirm each with probe.py)"); print(checked)


def load_prompt(name):
    return (PROMPTS / name).read_text()


if __name__ == "__main__":
    main()
