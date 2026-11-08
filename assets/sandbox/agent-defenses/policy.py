"""A per-task policy, checked before every tool call (a tiny reference monitor at the tool layer)."""


class PolicyViolation(Exception):
    pass


# Task: "summarize README.md". The task needs one file and no network.
SUMMARIZE_POLICY = {
    "read_file": lambda path: path == "README.md",
    "http_get": lambda url: False,
}


def check_summarize_task(tool, arg):
    rule = SUMMARIZE_POLICY.get(tool)
    if rule is None or not rule(arg):
        raise PolicyViolation(f"{tool}({arg!r}) is outside the task's policy")
