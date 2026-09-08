from flask import Flask, render_template, request, redirect, url_for, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, init_db, seed_db, close_db, \
    get_user_by_email, create_user, get_user_by_id

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

    user = {
        "name":         "Nitish Kumar",
        "email":        "nitish@example.com",
        "member_since": "August 2024",
        "initials":     "NK",
    }
    stats = {
        "total_spent":       "₹18,240",
        "transaction_count": 34,
        "top_category":      "Food",
    }
    transactions = [
        {"date": "09 Sep 2026", "description": "Monthly grocery run",  "category": "Food",          "amount": "₹2,350"},
        {"date": "08 Sep 2026", "description": "Electricity bill",      "category": "Bills",         "amount": "₹1,840"},
        {"date": "07 Sep 2026", "description": "Metro card top-up",     "category": "Transport",     "amount": "₹500"},
        {"date": "06 Sep 2026", "description": "Pharmacy",              "category": "Health",        "amount": "₹620"},
        {"date": "05 Sep 2026", "description": "Cinema — Pushpa 2",     "category": "Entertainment", "amount": "₹800"},
        {"date": "04 Sep 2026", "description": "New running shoes",     "category": "Shopping",      "amount": "₹3,499"},
        {"date": "03 Sep 2026", "description": "Breakfast at cafe",     "category": "Food",          "amount": "₹340"},
        {"date": "02 Sep 2026", "description": "Courier charges",       "category": "Other",         "amount": "₹180"},
    ]
    categories = [
        {"name": "Food",          "amount": "₹5,890", "percent": 32},
        {"name": "Bills",         "amount": "₹4,200", "percent": 23},
        {"name": "Shopping",      "amount": "₹3,499", "percent": 19},
        {"name": "Entertainment", "amount": "₹2,100", "percent": 12},
        {"name": "Transport",     "amount": "₹1,420", "percent":  8},
        {"name": "Health",        "amount": "₹870",   "percent":  5},
        {"name": "Other",         "amount": "₹261",   "percent":  1},
    ]
    return render_template("profile.html",
                           user=user, stats=stats,
                           transactions=transactions, categories=categories)


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
