# White-box step 2: extract the server constraints (S)

Below is the server code that handles the form's submission, including any
validation helpers, model hooks, or middleware it calls. List every check the server
applies to each request parameter before the parameter affects state or output.

Output one row per check:
| parameter | check | file:line |

Then list every request parameter the handler reads, including parameters read in
bulk (for example, `request.form` copied into a model). Mark a parameter "unchecked"
when no check applies. Report only checks you can point to in the code.

<paste the handler and the helpers it calls>
