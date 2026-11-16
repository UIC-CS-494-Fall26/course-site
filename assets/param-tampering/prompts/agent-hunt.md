# Agentic hunt: find parameter tampering in this repository

Read AGENTS.md (or CLAUDE.md) first and follow its rules.

Goal: find places where a form restricts an input in the browser and the server
accepts a value outside that restriction (web parameter tampering, CWE-472 / CWE-602).

The app runs at <http://127.0.0.1:PORT>. Work in this loop:
1. Find a form with a client-side restriction. Cite the template file and line.
2. Find the handler for that form. Cite the file and line. State which checks the handler applies.
3. If a restriction lacks a server check, confirm the gap with one request:
   `python3 ../scripts/replay.py http://127.0.0.1:PORT/<path> name=value ...`
4. Report each confirmed finding as a finding card (see below), then continue.

Finding card:
- form (file:line), parameter, client restriction
- server handler (file:line), missing check
- replay command and the response that shows the server accepted the value
- harm in one sentence

Report only findings you confirmed with a request. List unconfirmed hunches separately.
