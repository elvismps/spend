from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, init_db, seed_db, close_db, \
    get_user_by_email, create_user, get_user_by_id
import database.queries as queries

app = Flask(__name__)
app.secret_key = "dev-secret-change-in-prod"
app.teardown_appcontext(close_db)


@app.context_processor
def inject_current_user():
    user_id = session.get("user_id")
    return {"current_user": get_user_by_id(user_id) if user_id else None}


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name     = request.form.get("name", "").strip()
    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name:
        return render_template("register.html", error="Full name is required.")
    if not email:
        return render_template("register.html", error="Email address is required.")
    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters.")
    if get_user_by_email(email):
        return render_template("register.html", error="Email already registered.")

    password_hash = generate_password_hash(password)
    try:
        create_user(name, email, password_hash)
    except Exception:
        abort(500)

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email:
        return render_template("login.html", error="Email address is required.")
    if not password:
        return render_template("login.html", error="Password is required.")

    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.")

    session["user_id"] = user["id"]
    return redirect(url_for("landing"))


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    for d in (start_date, end_date):
        if d:
            try:
                datetime.strptime(d, "%Y-%m-%d")
            except ValueError:
                abort(400)

    if start_date and end_date and start_date > end_date:
        abort(400)

    if start_date and end_date:
        range_label = f"{start_date} – {end_date}"
    elif start_date:
        range_label = f"from {start_date}"
    elif end_date:
        range_label = f"until {end_date}"
    else:
        range_label = None

    uid = session["user_id"]
    user = queries.get_user_by_id(uid)
    stats = queries.get_summary_stats(uid, start_date=start_date or None, end_date=end_date or None)
    transactions = queries.get_recent_transactions(uid, start_date=start_date or None, end_date=end_date or None)
    categories = queries.get_category_breakdown(uid, start_date=start_date or None, end_date=end_date or None)
    return render_template("profile.html",
                           user=user, stats=stats,
                           transactions=transactions, categories=categories,
                           start_date=start_date, end_date=end_date,
                           range_label=range_label)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
