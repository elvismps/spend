import re
import database.queries as queries


# ------------------------------------------------------------------ #
# get_user_by_id                                                      #
# ------------------------------------------------------------------ #

def test_get_user_by_id_returns_correct_fields(app):
    with app.app_context():
        result = queries.get_user_by_id(1)
    assert result["name"] == "Demo User"
    assert result["email"] == "demo@spendly.com"
    assert result["initials"] == "DU"
    assert re.match(r"^[A-Z][a-z]+ \d{4}$", result["member_since"])


def test_get_user_by_id_none_for_missing(app):
    with app.app_context():
        result = queries.get_user_by_id(9999)
    assert result is None


# ------------------------------------------------------------------ #
# get_summary_stats                                                   #
# ------------------------------------------------------------------ #

def test_get_summary_stats_with_expenses(app):
    with app.app_context():
        result = queries.get_summary_stats(1)
    assert result["total_spent"] == "₹400.24"
    assert result["transaction_count"] == 8
    assert result["top_category"] == "Bills"


def test_get_summary_stats_no_expenses(app):
    with app.app_context():
        result = queries.get_summary_stats(9999)
    assert result["total_spent"] == "₹0.00"
    assert result["transaction_count"] == 0
    assert result["top_category"] == "—"


# ------------------------------------------------------------------ #
# get_recent_transactions                                             #
# ------------------------------------------------------------------ #

def test_get_recent_transactions_order_and_count(app):
    with app.app_context():
        result = queries.get_recent_transactions(1, limit=10)
    assert len(result) == 8
    assert result[0]["date"] == "07 Sep 2026"
    assert result[-1]["date"] == "01 Sep 2026"
    assert result[-1]["description"] == "Breakfast at cafe"
    assert result[-1]["category"] == "Food"
    assert result[-1]["amount"] == "₹12.50"


def test_get_recent_transactions_limit_respected(app):
    with app.app_context():
        result = queries.get_recent_transactions(1, limit=3)
    assert len(result) == 3


def test_get_recent_transactions_empty_for_no_expenses(app):
    with app.app_context():
        result = queries.get_recent_transactions(9999)
    assert result == []


# ------------------------------------------------------------------ #
# get_category_breakdown                                              #
# ------------------------------------------------------------------ #

def test_get_category_breakdown_order_and_format(app):
    with app.app_context():
        result = queries.get_category_breakdown(1)
    assert len(result) == 7
    assert result[0]["name"] == "Bills"
    assert result[0]["amount"] == "₹120.00"
    assert result[0]["percent"] == 34
    assert sum(cat["percent"] for cat in result) == 100
    assert result[-1]["name"] == "Other"


def test_get_category_breakdown_empty_for_no_expenses(app):
    with app.app_context():
        result = queries.get_category_breakdown(9999)
    assert result == []


def test_get_category_breakdown_all_keys_present(app):
    with app.app_context():
        result = queries.get_category_breakdown(1)
    for cat in result:
        assert set(cat.keys()) == {"name", "amount", "percent"}


# ------------------------------------------------------------------ #
# /profile route                                                      #
# ------------------------------------------------------------------ #

def test_profile_unauthenticated_redirects_to_login(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_authenticated_returns_200(client):
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    response = client.get("/profile")
    assert response.status_code == 200
    assert b"Demo User" in response.data
    assert b"demo@spendly.com" in response.data
    assert b"Bills" in response.data


def test_profile_authenticated_shows_real_stats(client):
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    response = client.get("/profile")
    assert "₹400.24".encode() in response.data
