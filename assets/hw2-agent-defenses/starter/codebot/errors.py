"""The one exception that every defense raises."""


class Blocked(Exception):
    """A defense refused a tool call. The agent sees the message and carries on.

    policy.check() and check_sink() raise Blocked. Harness.call() catches
    the exception and hands the model the text "BLOCKED: <message>" as the
    tool result.
    """
