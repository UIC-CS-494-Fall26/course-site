# Lab rules for coding agents

These rules apply to any coding agent (Claude Code, Codex CLI, Gemini CLI, Cursor, Copilot, OpenHands) in this lab.

- Send requests only to 127.0.0.1 or localhost. Never contact any other host.
- Test only the apps in targets/, at their pinned commits, running in local Docker.
- Read code freely. Modify no files inside the target repositories.
- Confirm every finding with scripts/probe.py (error or boolean mode), and quote the command and the output.
- Probes are read-only. Never send a stacked query, a DROP, a write, or any payload that changes data.
- Mark any claim without a file:line citation or a confirming probe as a hunch.
- Stop and report if a request could change or delete data in or outside the container.
