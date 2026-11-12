"""Part II: run every shell command inside a sandbox.

wrap() turns a shell command into the argv that the harness runs. Pick the
sandbox with CODEBOT_SANDBOX=macos or CODEBOT_SANDBOX=docker. The default is
macos on a Mac and docker everywhere else.

You write the sandbox itself in sandbox/run_shell.sb (macOS) or
sandbox/docker-run-shell.sh (Docker). This file needs no changes.
"""
import os
import sys
from pathlib import Path

# The folder with the two sandbox files.
SANDBOX_DIR = Path(__file__).resolve().parent.parent / "sandbox"


def wrap(command, ws):
    """Return the argv that runs command inside the sandbox, with ws as the workspace.

    An argv is the list form of a command line: ["ls", "-l"] runs "ls -l".

    macOS: sandbox-exec loads sandbox/run_shell.sb and passes ws as the
    parameter WS. The profile reads the parameter as (param "WS").

    Docker: sandbox/docker-run-shell.sh gets ws as its first argument and
    the command as its second.
    """
    if sys.platform == "darwin":  # "darwin" means macOS
        default = "macos"
    else:
        default = "docker"
    kind = os.environ.get("CODEBOT_SANDBOX", default)

    if kind == "macos":
        profile = str(SANDBOX_DIR / "run_shell.sb")
        return ["sandbox-exec", "-f", profile, "-D", f"WS={ws}", "/bin/sh", "-c", command]
    return ["sh", str(SANDBOX_DIR / "docker-run-shell.sh"), str(ws), command]
