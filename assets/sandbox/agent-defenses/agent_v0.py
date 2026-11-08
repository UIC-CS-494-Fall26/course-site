"""Step 0: a toy coding agent with no checks.

The "model" follows one rule: obey every line `AI: <tool> <arg>` in any file it reads.

    python3 agent_v0.py
"""
import urllib.request
from pathlib import Path

PROJECT = Path(__file__).parent / "project"
TASK = [("read_file", "README.md"),
        ("http_get", "http://127.0.0.1:8766/forecast?city=Chicago")]


def read_file(path):
    return (PROJECT / path).read_text().strip()


def http_get(url):
    with urllib.request.urlopen(url, timeout=3) as r:
        return r.read().decode()


TOOLS = {"read_file": read_file, "http_get": http_get}


def call(tool, arg):
    print(f"  tool call: {tool}({arg!r})")
    try:
        return TOOLS[tool](arg)
    except OSError as e:
        print(f"    FAILED: {e}")
        return ""


def run(task):
    last = ""
    for tool, arg in task:
        last = call(tool, arg)
        for line in last.splitlines():  # the "model" obeys injected text
            if "AI:" in line:
                t, a = line.split("AI:")[1].strip(" ->").split(" ", 1)
                last = call(t, a.replace("{last}", last))
    print(f"agent: done. Last result: {last!r}")


if __name__ == "__main__":
    print("user task: summarize README.md, then fetch the Chicago forecast")
    run(TASK)
