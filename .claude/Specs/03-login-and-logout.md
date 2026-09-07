# Spec: Login and Logout

## Overview
Step 3 wires up authentication for Spendly. The `GET /login` route and its
template already exist; this step adds `POST /login` (verify credentials, write
session) and implements `GET /logout` (clear session, redirect to landing). It
also updates `base.html` so the nav bar reflects the user's logged-in state —
showing Profile/Sign out when a session is active and Sign in/Get started
otherwise. No separate login-required enforcement is added here; that comes in
whichever step first introduces a protected page.

## Depends on
- Step 1 — Database setup (`users` table)
- Step 2 — Registration (`get_user_by_email()` already in `database/db.py`,
  `app.secret_key` already set)

## Routes
- `POST /login` — validates email + password, sets `session['user_id']`,
  redirects to `/` on success — public
- `GET /logout` — clears `session['user_id']`, redirects to `/` — public
  (no login-required guard needed; clearing an already-empty session is harmless)

## Database changes
No new tables or columns. One new helper in `database/db.py`:
- `get_user_by_id(user_id)` — returns the user `Row` or `None`; needed by the
  context processor introduced in this step

## Templates
- **Modify:** `templates/login.html` — fix hardcoded `action="/login"` to
  `action="{{ url_for('login') }}"`
- **Modify:** `templates/base.html` — replace the static Sign in / Get started
  nav links with a Jinja2 conditional that checks `session.get('user_id')`:
  - Logged in → Profile link + Sign out link
  - Logged out → Sign in link + Get started (CTA) link

## Files to change
- `app.py` — add `check_password_hash` import from werkzeug, add
  `get_user_by_id` to db import line, implement `POST /login`, implement
  `GET /logout`, add a `@app.context_processor` that injects `current_user`
  into every template
- `database/db.py` — add `get_user_by_id(user_id)`
- `templates/login.html` — fix hardcoded form action
- `templates/base.html` — session-aware nav

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use `sqlite3` via `get_db()` only
- Parameterised queries only — `?` placeholders, never f-strings in SQL
- Passwords verified with `werkzeug.security.check_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validation order for POST /login: email present → password present →
  user exists → password matches; return the first error found
- On invalid credentials use a generic message ("Invalid email or password.")
  — never reveal which field was wrong
- `session['user_id']` stores only the integer user id — nothing else
- `GET /logout` must call `session.clear()` (not just `session.pop`) so all
  session data is wiped regardless of what later steps store
- The context processor must call `get_user_by_id` only when
  `session.get('user_id')` is set — never query on every request for guests

## Definition of done
- [ ] Valid email + password → `session['user_id']` is set, redirects to `/`
- [ ] Wrong password → re-renders `/login` with "Invalid email or password."
- [ ] Unknown email → same generic error (does not reveal user existence)
- [ ] Blank email or password → re-renders with a visible error before any DB query
- [ ] Visiting `/logout` clears the session and redirects to `/`
- [ ] Nav shows "Sign in" and "Get started" for a guest
- [ ] Nav shows "Profile" and "Sign out" for a logged-in user
- [ ] `GET /login` still renders the empty form (no regression)
- [ ] No raw SQL in `app.py` — all queries in `database/db.py`
