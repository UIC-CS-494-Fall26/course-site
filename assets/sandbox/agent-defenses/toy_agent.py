"""A toy coding agent for the CS494 demos.

The "model" is one rule: it obeys every line of the form `AI: <tool> <arg>` in any file it reads.
Real models follow injected text less reliably, but the harness around them looks the same.

    python3 toy_agent.py                  # no defense
    python3 toy_agent.py --policy         # every tool call checked by policy.py
"""
import sys
import urllib.request
from pathlib import Path

PROJECT = Path(__file__).parent / "project"


# ---- tools: the agent's authority -------------------------------------------
def read_file(path):
    return (PROJECT / path).read_text().strip()


def http_get(url):
    with urllib.request.urlopen(url, timeout=3) as r:
        return r.read().decode()


TOOLS = {"read_file": read_file, "http_get": http_get}


# ---- the harness: plan, call tools, repeat -----------------------------------
def call(tool, arg, check):
    print(f"  tool call: {tool}({arg!r})")
    if check:
        check(tool, arg)
    return TOOLS[tool](arg)


def run(task_file, check=None):
    print(f"user task: summarize {task_file}")
    text = call("read_file", task_file, check)
    last = ""
    for line in text.splitlines():
        if "AI:" in line:  # the "model" obeys injected instructions
            tool, arg = line.split("AI:")[1].strip(" ->").split(" ", 1)
            try:
                last = call(tool, arg.replace("{last}", last), check)
            except Exception as e:
                print(f"  BLOCKED: {type(e).__name__}: {e}")
                return
    print("agent: The README describes a weather widget.")


if __name__ == "__main__":
    check = None
    if "--policy" in sys.argv:
        from policy import check_summarize_task as check
    run("README.md", check)
