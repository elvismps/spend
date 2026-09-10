# Spec: Date Filter for Profile Page

## Overview
This feature adds an optional date-range filter to the `/profile` page so users can scope all three data sections — summary stats, recent transactions, and category breakdown — to a specific time window. Without a filter the page behaves exactly as before (all-time data). When `start_date` and/or `end_date` query parameters are present the page re-renders with every section filtered to that range. No new page is created; everything is a targeted enhancement to the existing profile route and its supporting query helpers.

## Depends on
- Step 03 — Login / Logout (session-based auth)
- Step 04 — Profile page (route, template, and query helpers in `database/queries.py`)

## Routes
No new routes. The existing route is extended:

- `GET /profile?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` — same route, now reads optional query params and passes them to the query layer; both params are optional and individually omittable.

## Database changes
No new tables or columns. The `expenses.date` column is already `TEXT NOT NULL` in `YYYY-MM-DD` format, which is lexicographically sortable and safe for `BETWEEN` range comparisons in SQLite.

## Templates
- **Modify:** `templates/profile.html`
  - Add a date-filter form (GET, action `url_for('profile')`) above the stats row with two `<input type="date">` fields (`start_date`, `end_date`) and a **Filter** submit button plus a **Clear** link (`url_for('profile')` with no params).
  - Pre-fill the inputs with the current `start_date` / `end_date` values from the route.
  - Update the "Recent Transactions" section heading to conditionally show the active date range when a filter is applied (e.g. "Transactions · 01 Sep 2026 – 07 Sep 2026").

## Files to change
- `database/queries.py` — add optional `start_date` / `end_date` keyword args to `get_recent_transactions`, `get_summary_stats`, and `get_category_breakdown`; inject `AND date BETWEEN ? AND ?` only when those args are provided.
- `app.py` — update the `/profile` route to read `request.args.get('start_date')` and `request.args.get('end_date')`, validate their format (must be `YYYY-MM-DD` or empty string / None), pass them to all three query calls, and forward them to the template.
- `templates/profile.html` — add the filter form and conditional heading as described above.
- `static/css/profile.css` — add styles for the filter form (`date-filter-form`, `date-filter-inputs`, `date-filter-actions`) using existing CSS variables only.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only.
- Parameterised queries only — never build SQL with f-strings or string concatenation.
- The date filter is built with a standard HTML `<form method="GET">` — no JavaScript required for submission.
- Use CSS variables (`--ink`, `--accent`, `--paper`, `--radius-sm`, etc.) — never hardcode hex values.
- All templates extend `base.html`.
- Validation in the route: if a date param is present but not a valid `YYYY-MM-DD` string, abort with 400.
- When only one of `start_date` / `end_date` is supplied it is still applied (open-ended range): `date >= start_date` or `date <= end_date`.
- The limit on `get_recent_transactions` (default 10) is removed when a date filter is active — show all matching rows in the date range.
- Do not change the `get_user_by_id` function in `queries.py` — it has no date dimension.

## Definition of done
- [ ] Visiting `/profile` with no query params renders identically to the current behaviour (all-time stats, last 10 transactions).
- [ ] Visiting `/profile?start_date=2026-09-01&end_date=2026-09-05` shows only the 5 seed expenses in that range; stats and category bars reflect only those rows.
- [ ] Visiting `/profile?start_date=2026-09-07` (no end date) shows the two 2026-09-07 expenses and stats for those rows only.
- [ ] Visiting `/profile?end_date=2026-09-03` (no start date) shows the three expenses on or before 2026-09-03.
- [ ] The date inputs in the form are pre-filled with the active filter values after submission.
- [ ] Clicking "Clear" reloads `/profile` with no params and restores all-time data.
- [ ] Submitting an invalid date string (e.g. `start_date=notadate`) returns HTTP 400.
- [ ] The section heading updates to show the active date range when a filter is applied.
- [ ] All styles use CSS variables — no hardcoded colours.
- [ ] Existing tests continue to pass.
