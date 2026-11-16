# Parameter-tampering hunt: student kit

A tampering bug exists when a form restricts an input in the browser (hidden field,
`min`/`max`, a `<select>`, a `disabled` field, a JavaScript check) and the server
accepts a value outside that restriction. In this lab we meet the bug on a toy shop,
then hunt it in real open-source code with an LLM.

## Rules
- Send requests only to `127.0.0.1`. The apps run in local Docker, and
  `scripts/replay.py` refuses any other host.
- Read code freely. Change no files inside a target.
- Confirm every finding with a real request, and cite `file:line`.

Coding agents read these rules from `AGENTS.md` (or `CLAUDE.md`), which carry the
same text.

## Before class (about 15 minutes, needs a network)
1. Start Docker. On this course's machines: `colima start`.
2. Pull the apps that run in one container, and build the toy shop:
   ```
   docker compose -f targets/docker-compose.yml pull
   docker compose -f targets/docker-compose.yml build
   ```
3. Fetch the source for every target (for reading):
   ```
   bash scripts/fetch_targets.sh
   ```
4. Pick how you will run the LLM:
   - a chat window or a coding agent: nothing to install.
   - the fallback scripts: `pip install -r requirements.txt`, then set the key for
     your provider (see `scripts/_llm.py` for the model strings).

## In class
1. Start the apps:
   ```
   docker compose -f targets/docker-compose.yml up -d
   ```
   The toy shop is at http://127.0.0.1:8770 and Kanboard at http://127.0.0.1:8783
   (default login `admin` / `admin`).
2. Warm up: tamper with the toy shop in DevTools, then confirm from the terminal:
   ```
   python3 scripts/replay.py http://127.0.0.1:8770/order item=mug price=0.01 qty=1
   ```
3. Triage the targets, then hunt your pick with one of the two approaches.

## The targets
`targets/targets.yaml` lists all six, each pinned to a commit before a known,
already-fixed tampering CVE.

| Target | Runs live in class | What you hunt |
|---|---|---|
| toyshop | yes (warm-up) | hidden price, uncapped quantity, injected role |
| kanboard | yes | an invited user adds `role=app-admin` |
| rconfig | advanced, see `targets/rconfig/` | a non-admin sets their own role to Admin |
| ninja-forms | source only | a calculated total follows an unlisted option |
| wp-time-slots | source only | the server stores the client's posted total |
| shopizer | source only | a negative cart quantity |
| microweber | source only | a coupon applies after the admin turns coupons off |

"Source only" means you read the code and propose the bug with the white-box diff.
Kanboard is the shared target for a live confirmation with `replay.py`.

## The two approaches
- **White-box diff:** `prompts/extract-client.md`, `extract-server.md`, `diff.md`,
  or run `python3 scripts/whitebox.py --model <name> --form <f> --handler <h>`.
- **Agentic:** open your coding agent in this folder and paste `prompts/agent-hunt.md`.

## Scripts
- `scripts/replay.py` — send one form submission with chosen parameters (localhost only).
- `scripts/fetch_targets.sh` — clone or download every target's source at its pin.
- `scripts/triage.py` — score the targets for tampering risk (fallback for API users).
- `scripts/whitebox.py` — run the three white-box steps on one form and handler.
