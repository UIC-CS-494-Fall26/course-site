# Sink-trace step 1: find the query sinks

Below is application code. List every place a SQL query is built or executed: the sink.
A sink is any call that runs SQL (for example `db.execute`, `$wpdb->query`,
`$wpdb->get_results`, `mysqli_query`, `cursor.execute`) and the string handed to it.

Output one row per sink:
| sink call | file:line | how the query string is built (literal, concatenation, interpolation, prepare) |

Report only sinks you can point to in the code. Include sinks that look safe; we decide later.

<paste the handler files, or name the directory to read>
