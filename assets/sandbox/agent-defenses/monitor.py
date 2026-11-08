"""Step 4: a per-task policy, checked before every tool call."""


class Blocked(Exception):
    pass


POLICIES = {
    "summarize": {"read_file": lambda path: path == "README.md",
                  "http_get": lambda url: url.startswith("http://127.0.0.1:8766/")},
    "triage": {"read_file": lambda path: path in ("ISSUE-7.md", "secret.env"),
               "post_comment": lambda text: True},
}


def check(task, tool, arg):
    rule = POLICIES[task].get(tool)
    if rule is None or not rule(arg):
        raise Blocked(f"{tool}({arg!r}) is outside the {task!r} policy")
