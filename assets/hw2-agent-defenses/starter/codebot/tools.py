"""CodeBot's six tools. Every path stays inside the workspace.

The tools themselves carry no security checks. The harness (harness.py)
decides whether a call may run.
"""
import os
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path


class ToolError(Exception):
    """A tool failed, for example on a path outside the workspace. The model sees the message."""


class Env:
    """Where one run lives.

    run:      the run directory, .run/
    ws:       the workspace copy, .run/workspace/
    comments: the public comment log, .run/comments.log
    """

    def __init__(self, run_dir: Path):
        self.run = run_dir
        self.ws = run_dir / "workspace"
        self.comments = run_dir / "comments.log"


def workspace_path(env, path):
    """Return the absolute form of a workspace-relative path.

    A path that ends up outside the workspace raises ToolError. This rail
    keeps the agent in its folder. The rail plays no part in the defenses.
    """
    # resolve() makes the path absolute and removes ".." parts, so
    # "../secret.txt" turns into a real location outside the workspace.
    p = (env.ws / path).resolve()
    root = env.ws.resolve()
    # p.parents lists every folder above p. Inside the workspace, root is one of them.
    if p != root and root not in p.parents:
        raise ToolError(f"{path} lies outside the workspace")
    return p


def read_file(env, path):
    """Return the text of a workspace file."""
    return workspace_path(env, path).read_text()


def list_files(env, path="."):
    """Return every file under a workspace folder, one relative path per line, sorted."""
    base = workspace_path(env, path)
    names = []
    for p in base.rglob("*"):  # rglob("*") walks every file and folder under base
        if p.is_file():
            names.append(str(p.relative_to(env.ws)))
    return "\n".join(sorted(names))


def write_file(env, path, content):
    """Create or overwrite a workspace file, and create its parent folders when needed."""
    p = workspace_path(env, path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"wrote {len(content)} characters to {path}"


def run_shell(env, command, wrap=None):
    """Run a shell command in the workspace, and return its exit code and output.

    With no wrap, /bin/sh runs the command directly. With the sandbox on,
    the harness passes sandbox.wrap, which puts the command in a sandbox.
    """
    if wrap:
        argv = wrap(command, env.ws)
    else:
        argv = ["/bin/sh", "-c", command]

    # PYTHONDONTWRITEBYTECODE=1 keeps Python from leaving __pycache__ folders
    # in the workspace. {**os.environ, ...} copies the current environment
    # variables and adds this one.
    shell_env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

    # subprocess.run() runs a program and waits for the program to finish.
    # capture_output=True collects stdout and stderr, and text=True returns them as str.
    r = subprocess.run(argv, cwd=env.ws, capture_output=True, text=True,
                       timeout=60, env=shell_env)

    output = f"exit code {r.returncode}\n{r.stdout}{r.stderr}"
    return output[-4000:]  # keep the last 4000 characters


def http_get(env, url):
    """Fetch a URL on 127.0.0.1, and return the first 4000 characters of the body."""
    # urlparse() splits a URL into parts. .hostname is the part after "http://".
    host = urllib.parse.urlparse(url).hostname
    if host not in ("127.0.0.1", "localhost"):
        # A safety rail for the homework, not a defense: everything stays on your machine.
        raise ToolError("this homework allows requests to 127.0.0.1 only")

    # urlopen() sends a GET request. read() returns bytes, and decode() turns them into str.
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.read().decode()[:4000]


def post_comment(env, text):
    """Append a comment to .run/comments.log, the stand-in for a public issue tracker.

    Anyone may read a public comment, so the checker treats this log as a
    public place.
    """
    with open(env.comments, "a") as f:
        f.write(text + "\n---\n")
    print(f"    PUBLIC COMMENT: {text}")
    return "comment posted on the public issue tracker"


# Tool name -> function. Harness.call() looks up each tool here.
TOOLS = {
    "read_file": read_file,
    "list_files": list_files,
    "write_file": write_file,
    "run_shell": run_shell,
    "http_get": http_get,
    "post_comment": post_comment,
}

# Tool name -> parameter names, in order.
PARAMS = {
    "read_file": ["path"],
    "list_files": ["path"],
    "write_file": ["path", "content"],
    "run_shell": ["command"],
    "http_get": ["url"],
    "post_comment": ["text"],
}

# The tool descriptions that the real model reads.
DESCRIPTIONS = {
    "read_file": "Read a text file in the project.",
    "list_files": "List the files under a folder in the project.",
    "write_file": "Create or overwrite a text file in the project.",
    "run_shell": "Run a shell command in the project folder and return its output.",
    "http_get": "Fetch a URL with HTTP GET and return the body.",
    "post_comment": "Post a comment on the project's public issue tracker.",
}


def make_schema(name, params):
    """Describe one tool to the OpenAI API, in the API's JSON Schema format.

    Every parameter is a required string. strict=True makes the model fill
    in every parameter and nothing else.
    """
    properties = {}
    for p in params:
        properties[p] = {"type": "string"}
    return {
        "type": "function",
        "name": name,
        "description": DESCRIPTIONS[name],
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": params,
            "additionalProperties": False,
        },
        "strict": True,
    }


# The tool list that run_openai() sends to the model.
SCHEMAS = [make_schema(name, params) for name, params in PARAMS.items()]
