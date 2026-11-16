# White-box step 1: extract the client constraints (C)

Below is a form template and any JavaScript it loads. List every restriction the
browser places on each submitted parameter.

Output one row per restriction:
| parameter | restriction | source (HTML attribute, JS function, hidden/disabled/readonly, select options) | file:line |

Include parameters the form submits without user input (hidden fields).
Include parameters the form shows but never submits (disabled fields): note them as "not submitted".
Report only restrictions you can point to in the code.

<paste the form template and its JavaScript>
