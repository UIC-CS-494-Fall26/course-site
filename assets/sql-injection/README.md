# SQL-injection hunt: student kit

A SQL-injection bug exists when untrusted input (a request parameter, a form field, a
cookie, a header, or a stored row) reaches a database query built by string concatenation,
with no bound parameter or allowlist in between. In this lab we meet the bug on a toy app,
then hunt it in real open-source code with an LLM.

## Rules
- Send requests only to `127.0.0.1`. The apps run in local Docker, and `scripts/probe.py`
  refuses any other host.
- Probes are read-only: a lone quote or a true/false pair. No stacked queries, no writes.
- Read code freely. Change no files inside a target.
- Confirm every finding with a probe, and cite `file:line`.

Coding agents read these rules from `AGENTS.md` (or `CLAUDE.md`), which carry the same text.

## Before class (about 15 minutes, needs a network)
1. Start Docker. On your machines: `colima start`.
2. Build the toy app and pull the WordPress images:
   ```
   docker compose -f targets/docker-compose.yml build toydb
   docker compose -f targets/docker-compose.yml pull db wordpress
   ```
3. Fetch the source for every target (for reading):
   ```
   bash scripts/fetch_targets.sh
   ```
4. Pick how you will run the LLM:
   - a chat window or a coding agent: nothing to install.
   - the fallback scripts: `pip install -r requirements.txt`, then set the key for your
     provider (see `scripts/_llm.py` for the model strings).

## In class
1. Start the toy app:
   ```
   docker compose -f targets/docker-compose.yml up -d toydb
   ```
   It serves at http://127.0.0.1:8880.
2. Warm up: read a password out of the search box, then confirm from the terminal:
   ```
   python3 scripts/probe.py error "http://127.0.0.1:8880/search?q=QINJECT"
   ```
3. Triage the targets, then hunt your pick with one of the two approaches.

## The targets
`targets/targets.yaml` lists all six, each pinned before a known SQL-injection CVE.

| Target | Runs live in class | Injection point |
|---|---|---|
| toy app | yes (warm-up) | concatenated LIKE, login, ORDER BY |
| wp-polls | yes (shared warm-up, see `targets/README.md`) | a cookie |
| paid-member-subscriptions | source only | a request parameter |
| woo-product-filter | source only | the POST `filtersDataBackend` |
| wpdirectorykit | source only | `attribute_value` / `attribute_id` |
| forkcms | source only | a request parameter (standalone CMS) |

"Source only" means you read the code and propose the bug, then confirm against the
upstream fix. WP-Polls is the shared target for a live probe.

## The two approaches
- **Sink-trace:** `prompts/find-sinks.md`, `trace-source.md`, `check-parameterization.md`,
  or run `python3 scripts/whitebox.py --model <name> --file <f> --file <helper>`.
- **Agentic:** open your coding agent in this folder and paste `prompts/agent-hunt.md`.

## Scripts
- `scripts/probe.py` — confirm a finding safely (error or boolean mode, localhost only).
- `scripts/fetch_targets.sh` — download or clone every target's source at its pin.
- `scripts/triage.py` — score the targets for SQLi risk (fallback for API users).
- `scripts/whitebox.py` — run the three sink-trace steps on the files you pass.
