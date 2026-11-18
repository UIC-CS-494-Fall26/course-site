# Sink-trace step 2: trace each sink back to a source

Here is the list of sinks from step 1, and the surrounding code. For each sink, trace the
parts of the query string back to where they enter the program. A source is any untrusted
input: `$_GET`, `$_POST`, `$_COOKIE`, `$_SERVER`, `php://input`, a request object, or a
database row that earlier held user input (second-order).

Output one row per sink input:
| sink (file:line) | input expression | source (GET / POST / cookie / header / stored) | source file:line |

Mark an input "constant" when it does not come from a request. Report only what you can
point to in the code.

Sinks:
<paste step 1 output>

Code:
<paste the handlers and the helpers they call>
