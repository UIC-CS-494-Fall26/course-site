# White-box step 3: diff C against S

Here are two tables: the client constraints C and the server constraints S for the
same form. For every restriction in C, decide whether S enforces the same restriction.

Output one row per gap:
| parameter | client restriction | server check (or "missing") | tampered value to try | expected harm |

Also list parameters the server reads that the form never submits; an attacker can add them.
Then propose one `replay.py` command per gap.

C:
<paste step 1 output>

S:
<paste step 2 output>
