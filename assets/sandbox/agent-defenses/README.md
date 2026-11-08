# Agent defenses: live demos

Demo code for the CS494 agent-defenses lectures (`agent-defenses.md`, with the older `agent-defenses.v1.md`). A toy agent gets attacked, then fixed one step at a time. Every script runs offline: both servers listen on 127.0.0.1 only, so no data leaves the laptop.

The toy agent's "model" follows one rule: obey every line `AI: <tool> <arg>` in any file the agent reads. Real models follow injected text less reliably, but the harness around them looks the same.

## Requirements

- Python 3.10 or newer, standard library only.
- macOS for `sandbox-exec`. Apple marks the tool as deprecated, but the tool still runs on macOS 27.
- Docker for the container demo. Pull the image before class: `docker pull python:3.12-slim`.

## Before class

Start two servers, each in its own terminal, from this directory:

```sh
python3 listener.py      # the attacker, 127.0.0.1:8765; prints whatever reaches the server
python3 weather_api.py   # the legitimate service the task needs, 127.0.0.1:8766
```

## Lecture 1: lock down the agent

| Step | Command | What you should see |
|---|---|---|
| 1. Attack | `python3 agent_v0.py` | The listener prints `ATTACKER RECEIVED: /leak?k=API_KEY=sk-demo-4242`. The forecast still arrives. |
| 3. Sandbox (macOS) | `sandbox-exec -f deny-network.sb python3 agent_v0.py` | Both network calls fail with `Operation not permitted`. The leak stops, and so does the forecast. |
| 3. Sandbox (Docker) | `./docker-run.sh agent_v0.py` | Both network calls fail with `Connection refused`. |
| 4. Per-task policy | `python3 agent_v1.py` | `read_file('secret.env')` gets BLOCKED by `monitor.py`. The forecast arrives. |
| 5. Allowed calls leak | `python3 agent_v1.py triage` | Every call passes the policy, and the key appears as a `PUBLIC COMMENT`. |


| File | Role |
|---|---|
| `project/README.md` | The poisoned README (lecture 1, steps 1 to 4). |
| `project/ISSUE-7.md` | The poisoned issue (lecture 1, step 5, and lecture 2). |
| `project/secret.env` | A fake key, `sk-demo-4242`. |
| `agent_v0.py` | The agent with no checks. |
| `agent_v1.py`, `monitor.py` | The agent with a per-task policy checked before every tool call. |
| `deny-network.sb` | A three-line macOS sandbox profile that denies the network. |
| `docker-run.sh` | Runs an agent with `--network none` and a read-only mount. Defaults to `toy_agent.py`. |
| `listener.py`, `weather_api.py` | The attacker and the legitimate service. |
| `toy_agent.py`, `policy.py`, `taint.py` | The demos for v1 of the deck (`agent-defenses.v1.md`). |

