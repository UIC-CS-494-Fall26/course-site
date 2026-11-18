# Sink-trace step 3: check the path from source to sink

Here are the sinks and their sources. For each tainted input that reaches a sink, decide
how the code treats the value before the sink:

- **bound**: passed as a parameter / placeholder (`?`, `%s`, `:name`, `->prepare`). Safe.
- **allowlisted**: compared against a fixed set before use (the safe fix for an identifier
  such as a column in `ORDER BY`). Safe.
- **escaped only**: run through an escape or a blocklist, then concatenated. Weak; note it.
- **concatenated**: glued into the string with nothing in between. Injectable.

Output one row per tainted input:
| input | sink (file:line) | treatment | injectable? | a payload to try | context (string / numeric / identifier / LIKE) |

Then, for each injectable row, write one `probe.py` command (error or boolean mode) that
would confirm the bug against the running app. Report only what the code shows.

Sinks and sources:
<paste step 2 output, plus the relevant code>
