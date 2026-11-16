# rConfig (CVE-2026-63102) — advanced, optional

rConfig needs MySQL and a one-time install, so it takes more setup than Kanboard or
the toy shop. Treat it as a stretch target rather than the default hunt.

The attack is a role mass assignment: a logged-in non-admin user edits their own
account through `PATCH /api/users/{id}` with `role=Admin`, and the server accepts it.
The vulnerable file is `app/Http/Requests/StoreUserRequest.php`, where `authorize()`
returns `auth()->check()` and the `role` rule is only `required`.

The instructor key (`demos/param-tampering-key/README.md`) has the full standup: a
compose file with MySQL, the `php artisan v8core:install` step, the session, cache,
and Sanctum settings to adjust, and the exact request. One environment note: Docker
here runs on Colima, which does not mount the session temp dir, so bake the `.env`
into a small derived image rather than bind-mounting it.

The app serves on http://127.0.0.1:8784.
