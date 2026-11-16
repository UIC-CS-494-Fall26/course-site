# Triage: which app should we hunt first?

You are helping a security class pick a target for **web parameter tampering**.
A tampering bug exists when a form restricts an input in the browser (hidden field,
max/min, maxlength, select options, disabled or readonly field, JavaScript check)
and the server accepts a value outside that restriction.

For each repository below, read its form templates and request handlers, then score
it from 0 to 10 for tampering risk. Base the score on these signals:

1. Hidden fields that carry prices, totals, IDs, roles, or other state.
2. Validation written only in HTML attributes or JavaScript.
3. Handlers that copy request parameters straight into a model or query (mass assignment).
4. Money, quantity, permission, or ownership fields in forms.
5. A thin server layer with no shared validation library.

Output one table row per repository:
| repo | score | strongest signal | file:line of the best example |

Quote file paths and lines that exist. If you cannot find evidence for a signal, say "none found".

Repositories:
<paste the list from targets/targets.yaml>
