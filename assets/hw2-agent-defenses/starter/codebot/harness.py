"""The harness: every tool call the model asks for passes through Harness.call().

Defenses plug in here:
- policy  (Part II):  policy.check() runs before every call.
- sandbox (Part II):  run_shell runs inside sandbox.wrap().
- ifc     (Part III): label_source() labels every tool result, and
                      check_sink() checks every call against the context label.
"""
import json
import os
import subprocess

from . import policy, sandbox, tools
from .errors import Blocked
from .labels import PUBLIC_TRUSTED, Label, join, flows_to  # you need flows_to in check_sink

# The developer's own code and configuration. Everything else in the project
# may hold text from outsiders, such as a README edit or an issue report.
TRUSTED_DIRS = ["src", "tests", ".codebot"]


def is_trusted_path(path):
    """Return True for files in src/, tests/, and .codebot/: code and config the developer wrote.

    os.path.normpath() simplifies the path first, so "src/../README.md"
    becomes "README.md". Then only the first folder in the path counts.
    """
    first_folder = os.path.normpath(path).split(os.sep)[0]
    return first_folder in TRUSTED_DIRS


# ---------------------------------------------------------------- Part III ---

def label_source(tool, args, result) -> Label:
    """Return the label of a tool result. This is where labels get attached.

    tool:   the tool's name, such as "read_file".
    args:   the call's arguments, such as {"path": "README.md"}.
    result: the text the tool returned.

    Harness.call() joins the returned label into the context label after
    every successful call. The helper is_trusted_path() answers the
    question "src/, tests/, or .codebot/?" for read_file.

    TODO (Part III): follow the source table in the handout.
    """
    return PUBLIC_TRUSTED


def check_sink(tool, args, context: Label):
    """Raise Blocked when a call would send data somewhere its label may not go.

    The model wrote the arguments, and every token the model writes may depend
    on every token in its context. So the arguments carry the context label.

    tool:    the tool's name, such as "http_get".
    args:    the call's arguments, such as {"url": "http://..."}.
    context: the join of the labels of every tool result so far.

    Return None to allow the call. Use flows_to() to compare the context
    label with the label each sink may receive.

    TODO (Part III): follow the sink table in the handout.
    """
    return None


# ---------------------------------------------------------------- the loop ---

# A bad call from the model, such as a missing file or a wrong argument name,
# raises one of these errors. The model sees the error and may try again.
TOOL_ERRORS = (tools.ToolError, OSError, KeyError, TypeError, subprocess.SubprocessError)


class Harness:
    """Runs the model's tool calls for one task, under a chosen set of defenses.

    The harness keeps one context label: the join of the labels of every
    tool result the model has seen. The label starts at (public, trusted),
    because the user's task counts as public and trusted. The harness also
    writes one line per call to trace.jsonl.
    """

    def __init__(self, task, defenses, env, trace_path):
        """Set up the harness for one run.

        task:       "T1" to "T4". policy.check() looks up the task's policy.
        defenses:   a list with any of "policy", "sandbox", and "ifc".
        env:        the run's Env, from agent.fresh_run().
        trace_path: the file for one JSON record per tool call.
        """
        self.task = task
        self.defenses = defenses
        self.env = env
        self.context = PUBLIC_TRUSTED  # the user's task: public, trusted
        self.trace_path = trace_path
        open(trace_path, "a").close()  # create the trace file, even for a run with no calls

    def call(self, tool, args):
        """Run one tool call through the enabled defenses and return the result text.

        The steps run in this order:
        1. policy.check() may block the call (Part II).
        2. check_sink() may block the call, given the context label (Part III).
        3. The tool runs. With the sandbox on, run_shell runs inside sandbox.wrap().
        4. label_source() labels the result, and the context label absorbs that label.

        A block or a tool error ends the call early. The model then gets the
        text "BLOCKED: ..." or "ERROR: ..." as the result, and may try another
        call. Every call, blocked or not, gets one line in the trace.
        """
        print(f"  tool call: {tool}({shorten(args)})")
        record = {"tool": tool, "args": args}

        try:
            if tool not in tools.TOOLS:
                raise tools.ToolError(f"unknown tool {tool}")

            if "policy" in self.defenses:
                policy.check(self.task, tool, args)
            if "ifc" in self.defenses:
                check_sink(tool, args, self.context)

            result = self.run_tool(tool, args)

            if "ifc" in self.defenses:
                # Propagation: everything the model reads joins the context label.
                self.context = join(self.context, label_source(tool, args, result))
                record["context"] = str(self.context)

        except Blocked as e:
            result = f"BLOCKED: {e}"
            record["blocked"] = str(e)
            print(f"    {result}")
        except TOOL_ERRORS as e:
            result = f"ERROR: {e}"
            print(f"    {result}")

        record["result"] = result[:300]
        self.write_trace(record)
        return result

    def run_tool(self, tool, args):
        """Run the tool itself. Only run_shell takes the sandbox."""
        if tool == "run_shell":
            wrap = sandbox.wrap if "sandbox" in self.defenses else None
            return tools.run_shell(self.env, args["command"], wrap=wrap)
        # **args passes the dict as keyword arguments: read_file(env, path="README.md").
        return tools.TOOLS[tool](self.env, **args)

    def write_trace(self, record):
        """Append one call to the trace as a single line of JSON."""
        with open(self.trace_path, "a") as f:
            f.write(json.dumps(record) + "\n")


def shorten(args):
    """Return the arguments as JSON, cut to 120 characters for the console."""
    s = json.dumps(args)
    if len(s) < 120:
        return s
    return s[:117] + "..."
