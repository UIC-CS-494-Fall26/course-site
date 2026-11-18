# Triage: which app should we hunt first?

You are helping a security class pick a target for **SQL injection** (CWE-89).
A SQL-injection bug exists when untrusted input (a request parameter, a form field,
a cookie, a header, or a stored row) reaches a database query that is built by string
concatenation or interpolation, with no bound parameter or allowlist in between.

For each repository below, read its request handlers and the queries they build, then
score it from 0 to 10 for SQL-injection risk. Base the score on these signals:

1. Queries built by string concatenation, interpolation, or f-strings.
2. Request data (GET, POST, cookie, header, JSON) reaching a query.
3. `$wpdb->query`, `->get_results`, or `->get_var` called without `->prepare`.
4. A dynamic `ORDER BY`, table name, or column name.
5. Escaping or a blocklist used in place of a bound parameter.

Output one table row per repository:
| repo | score | strongest signal | file:line of the best example |

Quote file paths and lines that exist. If you cannot find evidence for a signal, say "none found".

Repositories:
<paste the list from targets/targets.yaml, or open targets/src/>
