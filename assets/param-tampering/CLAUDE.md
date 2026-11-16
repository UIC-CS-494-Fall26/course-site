# Lab rules for coding agents

These rules apply to any coding agent (Claude Code, Codex CLI, Gemini CLI, Cursor, Copilot, OpenHands) in this lab.

- Send requests only to 127.0.0.1 or localhost. Never contact any other host.
- Test only the apps in targets/, at their pinned commits, running in local Docker.
- Read code freely. Modify no files inside the target repositories.
- Confirm every finding with scripts/replay.py, and quote the command and the response.
- Mark any claim without a file:line citation or a confirming request as a hunch.
- Stop and report if a request could delete data outside the container.
