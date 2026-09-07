# Spec: Registration

## Overview
Step 2 adds user registration to Spendly. The `GET /register` route and its
template already exist; this step wires up the `POST /register` handler that
validates the submitted form, hashes the password, stores a new user row, and
redirects to the login page on success. It also adds the Flask `secret_key`
required for session support in later steps, and moves all user-related DB
logic into `database/db.py`.

## Depends on
- Step 1 — Database setup (`users` table created by `init_db()`)

## Routes
- `POST /register` — receives name/email/password from the registration form,
  validates input, checks email uniqueness, inserts the user, redirects to
  `/login` — public

## Database changes
No new tables or columns. Two new helper functions added to `database/db.py`:
- `get_user_by_email(email)` — returns a `Row` or `None`
- `create_user(name, email, password_hash)` — inserts and returns the new row's id

## Templates
- **Modify:** `templates/register.html` — already renders `{{ error }}`; no
  structural changes needed. Confirm `action="/register"` uses `url_for` style
  (currently hardcoded — fix to `{{ url_for('register') }}`).

## Files to change
- `app.py` — add `app.secret_key`, import `redirect/url_for/request/session/abort`
  from flask, convert `register()` to handle both GET and POST
- `database/db.py` — add `get_user_by_email()` and `create_user()`

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use `sqlite3` via `get_db()` only
- Parameterised queries only — `?` placeholders, never f-strings in SQL
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- `secret_key` must be set before any session usage; use a hard-coded dev
  string for now (e.g. `"dev-secret-change-in-prod"`) — a later step will
  move it to an env var
- Validation order: name present → email present → password ≥ 8 chars →
  email not already registered; return the first error found
- On success: redirect to `url_for('login')` — do NOT set `session['user_id']`
  here (that belongs to the login step)
- Use `abort(500)` if the DB insert fails unexpectedly

## Definition of done
- [ ] Submitting the form with all valid fields creates a new row in `users`
      and redirects to `/login`
- [ ] Submitting with a blank name re-renders `/register` with a visible error
- [ ] Submitting with a blank or malformed email re-renders with a visible error
- [ ] Submitting with a password shorter than 8 characters re-renders with error
- [ ] Submitting with an email that already exists re-renders with "Email already
      registered" error
- [ ] Password stored in DB is a bcrypt/werkzeug hash, not plaintext
- [ ] `GET /register` still works (renders the empty form, no regression)
- [ ] No raw SQL strings in `app.py` — all queries live in `database/db.py`
