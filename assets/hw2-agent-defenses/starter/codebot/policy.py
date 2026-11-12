"""Part II: a per-task policy, checked before every tool call.

A policy is plain data. POLICIES maps each task to the tools the task may
call. Each tool maps to its allowed arguments: for each argument name, a list
of allowed values.

    "T1": {
        "read_file": {"path": ["README.md"]},
    },

The policy above reads: in T1, the agent may call read_file, and only with
path "README.md". Every other call in T1 gets blocked.

Three more rules:
- An argument left out of the policy may take any value. So "post_comment": {}
  allows a comment with any text.
- A value may hold the wildcards * and ?, as in a shell. So "src/*" allows
  every path under src/.
- Before the check, a path loses any "./" or "x/.." parts. So "src/../.env"
  counts as ".env", and "src/*" refuses the path.

The argument names: read_file and list_files take path, write_file takes path
and content, run_shell takes command, http_get takes url, and post_comment
takes text.
"""
import os
from fnmatch import fnmatchcase

from .errors import Blocked

POLICIES = {
    "T1": {
        "read_file": {"path": ["README.md"]},
    },
    "T2": {},  # TODO (Part II)
    "T3": {},  # TODO (Part II)
    "T4": {},  # TODO (Part II)
}


def check(task, tool, args):
    """Raise Blocked unless the task's policy allows this call.

    A call passes only when the task's policy names the tool, and every
    argument listed in the policy matches one of its allowed values. Every
    other call gets blocked, so each policy works as an allowlist.
    """
    allowed_args = POLICIES[task].get(tool)
    if allowed_args is None:
        raise Blocked(f"policy: {task} never calls {tool}")

    for name, patterns in allowed_args.items():
        value = args.get(name)
        if value is None:
            raise Blocked(f"policy: in {task}, {tool} needs the argument {name}")
        if name == "path":
            # normpath() simplifies a path: "./src/../.env" becomes ".env".
            value = os.path.normpath(value)
        if not matches_any(value, patterns):
            raise Blocked(f"policy: in {task}, {tool} may not take {name}={args[name]!r}")


def matches_any(value, patterns):
    """Return True when value matches at least one pattern.

    fnmatchcase() matches shell-style patterns: "*" stands for any text and
    "?" for any one character. A pattern with no wildcards must match exactly.
    """
    for pattern in patterns:
        if fnmatchcase(value, pattern):
            return True
    return False
