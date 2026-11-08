"""Step 4: the same agent, with a monitor between the model and the tools.

    python3 agent_v1.py                 # task: summarize README.md, fetch the forecast
    python3 agent_v1.py triage          # task: triage ISSUE-7.md
"""
import sys
import urllib.request
from pathlib import Path
from monitor import Blocked, check

PROJECT = Path(__file__).parent / "project"
TASKS = {
    "summarize": [("read_file", "README.md"),
                  ("http_get", "http://127.0.0.1:8766/forecast?city=Chicago")],
    "triage": [("read_file", "ISSUE-7.md"),
               ("read_file", "secret.env"),  # the task checks that the key is configured
               ("post_comment", "Triaged: reproduced on Safari 18.")],
}


def read_file(path):
    return (PROJECT / path).read_text().strip()


def http_get(url):
    with urllib.request.urlopen(url, timeout=3) as r:
        return r.read().decode()


def post_comment(text):  # the issue tracker is public
    print(f"    PUBLIC COMMENT: {text}")
    return "posted"


TOOLS = {"read_file": read_file, "http_get": http_get, "post_comment": post_comment}


def call(task, tool, arg):
    print(f"  tool call: {tool}({arg!r})")
    try:
        check(task, tool, arg)  # the monitor: outside the model, on every call
        return TOOLS[tool](arg)
    except (Blocked, OSError) as e:
        print(f"    {'BLOCKED' if isinstance(e, Blocked) else 'FAILED'}: {e}")
        return ""


def run(task):
    last = ""
    for tool, arg in TASKS[task]:
        last = call(task, tool, arg)
        for line in last.splitlines():  # the "model" obeys injected text
            if "AI:" in line:
                t, a = line.split("AI:")[1].strip(" ->").split(" ", 1)
                last = call(task, t, a.replace("{last}", last))
    print(f"agent: done. Last result: {last!r}")


if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "summarize"
    print(f"user task: {task}")
    run(task)
