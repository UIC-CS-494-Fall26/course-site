# CodeBot: CS494 Homework 2 starter

CodeBot is a minimal coding agent for the homework *Lock down CodeBot*. The handout explains the four parts. This file covers setup and the commands you need.

## Requirements

- Python 3.11 or newer.
- The `openai` package and your own OpenAI API key, for Part I only.
- For the sandbox in Part II: macOS (`sandbox-exec` ships with macOS) or Docker (any OS).

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...       # never commit this key
```

Start the two local servers in a second terminal, and leave them running:

```sh
python3 servers/servers.py
```

- `127.0.0.1:9765` plays the attacker. Every request lands in `.run/listener.log`.
- `127.0.0.1:9766` plays the docs service that task T4 needs.

## Running CodeBot

```sh
python3 -m codebot.agent --task T1                       # scripted model, no defenses
python3 -m codebot.agent --task T2 --model openai        # the real LLM
python3 -m codebot.agent --attack attacks/samples/leak_readme.md
python3 -m codebot.agent --attack attacks/a_leak.md --model openai
python3 -m codebot.agent --task T3 --defenses policy,ifc,sandbox
```

Every run starts from a fresh copy of `workspace/` in `.run/workspace/`, with a new canary key in `.env`. A run leaves three files in `.run/`: `trace.jsonl` (every tool call), `comments.log` (every public comment), and `listener.log` (every request to the attacker).

The last line reports the outcome:

```
RESULT {"leak": ["listener"], "corrupted": false, "task_ok": true}
```

## Files

| File | Role | You edit |
|---|---|---|
| `codebot/agent.py` | Command line, tasks, and a fresh run directory for every run | no |
| `codebot/models.py` | The real LLM loop and the scripted model | no |
| `codebot/tools.py` | The six tools | no |
| `codebot/harness.py` | Every tool call passes through `Harness.call()` | Part III: `label_source`, `check_sink` |
| `codebot/labels.py` | The label lattice | Part III: `join`, `flows_to` |
| `codebot/policy.py` | Per-task policies | Part II: T2, T3, T4 |
| `codebot/sandbox.py` | Wraps every shell command in a sandbox | no |
| `sandbox/run_shell.sb` | The macOS sandbox profile | Part II (macOS) |
| `sandbox/docker-run-shell.sh` | The Docker sandbox | Part II (Docker) |
| `codebot/check.py` | Leak, corruption, and task checks | no |
| `servers/servers.py` | The attacker and the docs service | no |
| `workspace/` | The `tinycalc` project that CodeBot works on | no |
| `attacks/samples/` | Three sample attacks for the scripted model | no |
| `attacks/` | Your Part I attacks and traces | Part I |
| `tests/test_public.py` | The public tests | no |

Choose the sandbox with `CODEBOT_SANDBOX=macos` or `CODEBOT_SANDBOX=docker`. The default is macOS on a Mac and Docker everywhere else. Pull the Docker image once before you start: `docker pull python:3.12-slim`.

## Tests

```sh
python3 -m unittest tests.test_public -v
```

The tests use the scripted model and start the servers when needed. The starter fails most tests on purpose.

## Troubleshooting

- **`Address already in use`:** an older server still holds the port. Stop that server with `pkill -f servers/servers.py`.
- **`Connection refused` with no defenses on:** the servers stopped. Start the servers again.
- **The real LLM ignores your payload:** this outcome counts as normal. Try a payload that looks like part of the file: a maintainer note, a setup step, or a comment for bots.
