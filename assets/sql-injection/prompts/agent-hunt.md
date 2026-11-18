# Agentic hunt: find SQL injection in this repository

Read AGENTS.md (or CLAUDE.md) first and follow its rules.

Goal: find a place where untrusted input reaches a database query with no bound parameter
or allowlist (SQL injection, CWE-89). The app runs at <http://127.0.0.1:PORT>.

Work in this loop:
1. Find a query built from request data. Cite the file and line of the sink.
2. Name the source (GET / POST / cookie / header / stored) and show the path to the sink.
3. Confirm with one safe probe:
   `python3 ../scripts/probe.py error "http://127.0.0.1:PORT/<path>?x=QINJECT"`
   or the boolean mode. Put QINJECT where the payload goes.
4. Report each confirmed finding as a finding card (below), then continue.

Finding card:
- endpoint, source (file:line), sink (file:line), how the query is built
- the missing defense (bound parameter or allowlist)
- the probe command and the output that shows the server treats the input as SQL
- harm in one sentence

Probes are read-only: a lone quote or a true/false pair. Never send a stacked query, a
DROP, a write, or anything that changes data. Report only findings you confirmed with a
probe. List unconfirmed hunches separately.
