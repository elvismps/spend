"""
tests/test_date_filter.py

Pytest tests for the date-range filter on the /profile page.

Covers:
  - HTTP-layer behaviour (route, status codes, template output)
  - Query-layer behaviour (get_recent_transactions, get_summary_stats,
    get_category_breakdown) with start_date / end_date params

Seed data (demo@spendly.com / demo123, user_id=1):
  2026-09-01  Food          ₹12.50   "Breakfast at cafe"
  2026-09-02  Transport     ₹45.00   "Monthly bus pass top-up"
  2026-09-03  Bills        ₹120.00   "Electricity bill"
  2026-09-04  Health        ₹35.00   "Pharmacy"
  2026-09-05  Entertainment ₹60.00   "Cinema tickets"
  2026-09-06  Shopping      ₹89.99   "New headphones"
  2026-09-07  Other         ₹15.75   "Miscellaneous"
  2026-09-07  Food          ₹22.00   "Lunch with colleague"
  Total: ₹400.24  (8 transactions)
"""

import database.queries as queries


# ------------------------------------------------------------------ #
# Helper                                                              #
# ------------------------------------------------------------------ #

def _login_demo(client):
    """Log in as the seeded demo user."""
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})


# ================================================================== #
# HTTP-layer tests                                                    #
# ================================================================== #


# ------------------------------------------------------------------ #
# No filter — all-time data                                           #
# ------------------------------------------------------------------ #

def test_profile_no_filter_returns_200(client):
    _login_demo(client)
    response = client.get("/profile")
    assert response.status_code == 200, "Expected 200 for authenticated /profile with no filter"


def test_profile_no_filter_shows_total_spent(client):
    _login_demo(client)
    response = client.get("/profile")
    assert "₹400.24".encode() in response.data, \
        "Expected all-time total_spent ₹400.24 on unfiltered profile"


def test_profile_no_filter_top_category_is_bills(client):
    _login_demo(client)
    response = client.get("/profile")
    assert b"Bills" in response.data, "Expected Bills as all-time top category"


def test_profile_no_filter_heading_is_recent_transactions(client):
    _login_demo(client)
    response = client.get("/profile")
    assert b"Recent Transactions" in response.data, \
        "Heading should read 'Recent Transactions' when no filter is active"


def test_profile_no_filter_all_seed_descriptions_present(client):
    _login_demo(client)
    response = client.get("/profile")
    for description in [
        b"Breakfast at cafe",
        b"Monthly bus pass top-up",
        b"Electricity bill",
        b"Pharmacy",
        b"Cinema tickets",
        b"New headphones",
        b"Miscellaneous",
        b"Lunch with colleague",
    ]:
        assert description in response.data, \
            f"Expected description {description!r} in unfiltered profile"


def test_profile_no_filter_clear_link_absent(client):
    _login_demo(client)
    response = client.get("/profile")
    assert b"profile-filter-clear" not in response.data, \
        "Clear link should not be rendered when no filter is active"


# ------------------------------------------------------------------ #
# start_date + end_date                                               #
# ------------------------------------------------------------------ #

def test_profile_start_and_end_date_returns_200(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-01&end_date=2026-09-05")
    assert response.status_code == 200


def test_profile_start_and_end_date_correct_total_spent(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-01&end_date=2026-09-05")
    assert "₹272.50".encode() in response.data, \
        "Expected total_spent ₹272.50 for Sep 01–05"


def test_profile_start_and_end_date_top_category_bills(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-01&end_date=2026-09-05")
    assert b"Bills" in response.data, \
        "Expected Bills as top category for Sep 01–05 (₹120 is the largest)"


def test_profile_start_and_end_date_in_range_descriptions_present(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-01&end_date=2026-09-05")
    for description in [
        b"Breakfast at cafe",
        b"Monthly bus pass top-up",
        b"Electricity bill",
        b"Pharmacy",
        b"Cinema tickets",
    ]:
        assert description in response.data, \
            f"Expected in-range description {description!r} to appear"


def test_profile_start_and_end_date_out_of_range_descriptions_absent(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-01&end_date=2026-09-05")
    assert b"New headphones" not in response.data, \
        "Shopping (Sep 06) should be excluded when end_date=2026-09-05"
    assert b"Miscellaneous" not in response.data, \
        "Other (Sep 07) should be excluded when end_date=2026-09-05"
    assert b"Lunch with colleague" not in response.data, \
        "Food (Sep 07) should be excluded when end_date=2026-09-05"


def test_profile_start_and_end_date_heading_no_longer_recent(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-01&end_date=2026-09-05")
    assert b"Recent Transactions" not in response.data, \
        "Heading should NOT be 'Recent Transactions' when date filter is active"
    assert b"Transactions" in response.data, \
        "Heading should contain 'Transactions' when date filter is active"


def test_profile_start_and_end_date_inputs_prefilled(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-01&end_date=2026-09-05")
    assert b'value="2026-09-01"' in response.data, \
        "start_date input should be pre-filled with the provided value"
    assert b'value="2026-09-05"' in response.data, \
        "end_date input should be pre-filled with the provided value"


def test_profile_start_and_end_date_clear_link_present(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-01&end_date=2026-09-05")
    assert b'href="/profile"' in response.data, \
        "Clear link (href='/profile') should be rendered when filter is active"
    assert b"profile-filter-clear" in response.data, \
        "Clear link element with class 'profile-filter-clear' should be present"


# ------------------------------------------------------------------ #
# start_date only                                                     #
# ------------------------------------------------------------------ #

def test_profile_start_date_only_returns_200(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-07")
    assert response.status_code == 200


def test_profile_start_date_only_correct_total_spent(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-07")
    assert "₹37.75".encode() in response.data, \
        "Expected total_spent ₹37.75 for start_date=2026-09-07 (Other ₹15.75 + Food ₹22.00)"


def test_profile_start_date_only_sep07_descriptions_present(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-07")
    assert b"Miscellaneous" in response.data, "Other (Sep 07) should be included"
    assert b"Lunch with colleague" in response.data, "Food (Sep 07) should be included"


def test_profile_start_date_only_earlier_descriptions_absent(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-07")
    assert b"New headphones" not in response.data, \
        "Shopping (Sep 06) should be excluded when start_date=2026-09-07"
    assert b"Cinema tickets" not in response.data, \
        "Entertainment (Sep 05) should be excluded when start_date=2026-09-07"
    assert b"Breakfast at cafe" not in response.data, \
        "Food (Sep 01) should be excluded when start_date=2026-09-07"


def test_profile_start_date_only_heading_no_longer_recent(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-07")
    assert b"Recent Transactions" not in response.data
    assert b"Transactions" in response.data


def test_profile_start_date_only_input_prefilled(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-07")
    assert b'value="2026-09-07"' in response.data, \
        "start_date input should be pre-filled when only start_date provided"


def test_profile_start_date_only_clear_link_present(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-07")
    assert b"profile-filter-clear" in response.data, \
        "Clear link should be rendered when start_date is provided"


# ------------------------------------------------------------------ #
# end_date only                                                       #
# ------------------------------------------------------------------ #

def test_profile_end_date_only_returns_200(client):
    _login_demo(client)
    response = client.get("/profile?end_date=2026-09-03")
    assert response.status_code == 200


def test_profile_end_date_only_correct_total_spent(client):
    _login_demo(client)
    response = client.get("/profile?end_date=2026-09-03")
    assert "₹177.50".encode() in response.data, \
        "Expected total_spent ₹177.50 for end_date=2026-09-03 (Food+Transport+Bills)"


def test_profile_end_date_only_early_descriptions_present(client):
    _login_demo(client)
    response = client.get("/profile?end_date=2026-09-03")
    assert b"Breakfast at cafe" in response.data
    assert b"Monthly bus pass top-up" in response.data
    assert b"Electricity bill" in response.data


def test_profile_end_date_only_later_descriptions_absent(client):
    _login_demo(client)
    response = client.get("/profile?end_date=2026-09-03")
    assert b"Pharmacy" not in response.data, \
        "Health (Sep 04) should be excluded when end_date=2026-09-03"
    assert b"Cinema tickets" not in response.data, \
        "Entertainment (Sep 05) should be excluded when end_date=2026-09-03"
    assert b"New headphones" not in response.data, \
        "Shopping (Sep 06) should be excluded when end_date=2026-09-03"


def test_profile_end_date_only_heading_no_longer_recent(client):
    _login_demo(client)
    response = client.get("/profile?end_date=2026-09-03")
    assert b"Recent Transactions" not in response.data
    assert b"Transactions" in response.data


def test_profile_end_date_only_input_prefilled(client):
    _login_demo(client)
    response = client.get("/profile?end_date=2026-09-03")
    assert b'value="2026-09-03"' in response.data, \
        "end_date input should be pre-filled when only end_date provided"


def test_profile_end_date_only_clear_link_present(client):
    _login_demo(client)
    response = client.get("/profile?end_date=2026-09-03")
    assert b"profile-filter-clear" in response.data, \
        "Clear link should be rendered when end_date is provided"


# ------------------------------------------------------------------ #
# Validation errors — HTTP 400                                        #
# ------------------------------------------------------------------ #

def test_profile_invalid_start_date_string_returns_400(client):
    _login_demo(client)
    response = client.get("/profile?start_date=notadate")
    assert response.status_code == 400, "Expected 400 for non-date start_date value"


def test_profile_invalid_end_date_string_returns_400(client):
    _login_demo(client)
    response = client.get("/profile?end_date=badvalue")
    assert response.status_code == 400, "Expected 400 for non-date end_date value"


def test_profile_wrong_date_format_start_date_returns_400(client):
    """DD-MM-YYYY is not the expected YYYY-MM-DD format."""
    _login_demo(client)
    response = client.get("/profile?start_date=01-09-2026")
    assert response.status_code == 400, \
        "Expected 400 for start_date in DD-MM-YYYY format (wrong format)"


def test_profile_wrong_date_format_end_date_returns_400(client):
    _login_demo(client)
    response = client.get("/profile?end_date=03-09-2026")
    assert response.status_code == 400, \
        "Expected 400 for end_date in DD-MM-YYYY format (wrong format)"


def test_profile_partial_date_start_returns_400(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09")
    assert response.status_code == 400, "Expected 400 for partial date 'YYYY-MM'"


def test_profile_partial_date_end_returns_400(client):
    _login_demo(client)
    response = client.get("/profile?end_date=2026")
    assert response.status_code == 400, "Expected 400 for partial date 'YYYY'"


def test_profile_both_invalid_dates_returns_400(client):
    _login_demo(client)
    response = client.get("/profile?start_date=abc&end_date=xyz")
    assert response.status_code == 400, "Expected 400 when both date params are invalid"


def test_profile_valid_start_and_invalid_end_returns_400(client):
    _login_demo(client)
    response = client.get("/profile?start_date=2026-09-01&end_date=not-a-date")
    assert response.status_code == 400, \
        "Expected 400 when end_date is invalid even if start_date is valid"


# ================================================================== #
# Query-layer tests                                                   #
# ================================================================== #


# ------------------------------------------------------------------ #
# get_recent_transactions with date params                            #
# ------------------------------------------------------------------ #

def test_get_recent_transactions_start_and_end_date_count(app):
    """Sep 01–05 should return exactly 5 rows."""
    with app.app_context():
        result = queries.get_recent_transactions(
            1, limit=10, start_date="2026-09-01", end_date="2026-09-05"
        )
    assert len(result) == 5, \
        f"Expected 5 transactions for Sep 01–05, got {len(result)}"


def test_get_recent_transactions_date_filter_drops_limit(app):
    """When a date filter is active, the LIMIT clause is dropped regardless of the limit param."""
    with app.app_context():
        # Without filter, limit=3 should return only 3 rows
        limited = queries.get_recent_transactions(1, limit=3)
        # Full date range with limit=3: should return all 8 rows (LIMIT ignored)
        full_range = queries.get_recent_transactions(
            1, limit=3, start_date="2026-09-01", end_date="2026-09-07"
        )
    assert len(limited) == 3, "Without filter, limit=3 should yield 3 rows"
    assert len(full_range) == 8, \
        "With full-range date filter, LIMIT is dropped — expected all 8 rows"


def test_get_recent_transactions_start_date_only_count(app):
    with app.app_context():
        result = queries.get_recent_transactions(1, start_date="2026-09-07")
    assert len(result) == 2, \
        "Expected 2 transactions from 2026-09-07 onward (Other + Food)"


def test_get_recent_transactions_start_date_only_all_on_correct_date(app):
    with app.app_context():
        result = queries.get_recent_transactions(1, start_date="2026-09-07")
    dates = {tx["date"] for tx in result}
    assert dates == {"07 Sep 2026"}, \
        f"All returned transactions should be on Sep 07, got dates: {dates}"


def test_get_recent_transactions_end_date_only_count(app):
    with app.app_context():
        result = queries.get_recent_transactions(1, end_date="2026-09-03")
    assert len(result) == 3, \
        "Expected 3 transactions up to 2026-09-03 (Food + Transport + Bills)"


def test_get_recent_transactions_end_date_only_all_on_or_before_cutoff(app):
    with app.app_context():
        result = queries.get_recent_transactions(1, end_date="2026-09-03")
    valid_dates = {"01 Sep 2026", "02 Sep 2026", "03 Sep 2026"}
    for tx in result:
        assert tx["date"] in valid_dates, \
            f"Unexpected transaction date outside range: {tx['date']}"


def test_get_recent_transactions_date_order_desc_with_filter(app):
    """ORDER BY date DESC, id DESC should be preserved when filter is active."""
    with app.app_context():
        result = queries.get_recent_transactions(
            1, start_date="2026-09-01", end_date="2026-09-07"
        )
    assert result[0]["date"] == "07 Sep 2026", \
        "First result should be the latest date (Sep 07)"
    assert result[-1]["date"] == "01 Sep 2026", \
        "Last result should be the earliest date (Sep 01)"


def test_get_recent_transactions_amounts_formatted_with_filter(app):
    """Amounts should carry the ₹ prefix and two decimal places."""
    with app.app_context():
        result = queries.get_recent_transactions(1, start_date="2026-09-07")
    amounts = {tx["amount"] for tx in result}
    assert "₹15.75" in amounts, "Expected ₹15.75 for Other expense"
    assert "₹22.00" in amounts, "Expected ₹22.00 for Food expense"


def test_get_recent_transactions_empty_range_returns_empty_list(app):
    with app.app_context():
        result = queries.get_recent_transactions(
            1, start_date="2025-01-01", end_date="2025-01-31"
        )
    assert result == [], \
        "Expected empty list for a date range containing no expenses"


def test_get_recent_transactions_correct_descriptions_sep01_to_sep05(app):
    with app.app_context():
        result = queries.get_recent_transactions(
            1, start_date="2026-09-01", end_date="2026-09-05"
        )
    descriptions = {tx["description"] for tx in result}
    assert descriptions == {
        "Breakfast at cafe",
        "Monthly bus pass top-up",
        "Electricity bill",
        "Pharmacy",
        "Cinema tickets",
    }, f"Unexpected descriptions for Sep 01–05: {descriptions}"


# ------------------------------------------------------------------ #
# get_summary_stats with date params                                  #
# ------------------------------------------------------------------ #

def test_get_summary_stats_start_and_end_date_total(app):
    with app.app_context():
        result = queries.get_summary_stats(
            1, start_date="2026-09-01", end_date="2026-09-05"
        )
    assert result["total_spent"] == "₹272.50", \
        f"Expected ₹272.50 for Sep 01–05, got {result['total_spent']}"


def test_get_summary_stats_start_and_end_date_count(app):
    with app.app_context():
        result = queries.get_summary_stats(
            1, start_date="2026-09-01", end_date="2026-09-05"
        )
    assert result["transaction_count"] == 5, \
        f"Expected 5 transactions for Sep 01–05, got {result['transaction_count']}"


def test_get_summary_stats_start_and_end_date_top_category(app):
    with app.app_context():
        result = queries.get_summary_stats(
            1, start_date="2026-09-01", end_date="2026-09-05"
        )
    assert result["top_category"] == "Bills", \
        f"Expected Bills as top category for Sep 01–05, got {result['top_category']}"


def test_get_summary_stats_start_date_only_total(app):
    with app.app_context():
        result = queries.get_summary_stats(1, start_date="2026-09-07")
    assert result["total_spent"] == "₹37.75", \
        f"Expected ₹37.75 for Sep 07 only, got {result['total_spent']}"


def test_get_summary_stats_start_date_only_count(app):
    with app.app_context():
        result = queries.get_summary_stats(1, start_date="2026-09-07")
    assert result["transaction_count"] == 2, \
        f"Expected 2 transactions on Sep 07, got {result['transaction_count']}"


def test_get_summary_stats_start_date_only_top_category(app):
    """Food (₹22.00) > Other (₹15.75) so Food should be top on Sep 07."""
    with app.app_context():
        result = queries.get_summary_stats(1, start_date="2026-09-07")
    assert result["top_category"] == "Food", \
        f"Expected Food as top category on Sep 07, got {result['top_category']}"


def test_get_summary_stats_end_date_only_total(app):
    with app.app_context():
        result = queries.get_summary_stats(1, end_date="2026-09-03")
    assert result["total_spent"] == "₹177.50", \
        f"Expected ₹177.50 for Sep 01–03, got {result['total_spent']}"


def test_get_summary_stats_end_date_only_count(app):
    with app.app_context():
        result = queries.get_summary_stats(1, end_date="2026-09-03")
    assert result["transaction_count"] == 3, \
        f"Expected 3 transactions up to Sep 03, got {result['transaction_count']}"


def test_get_summary_stats_end_date_only_top_category(app):
    with app.app_context():
        result = queries.get_summary_stats(1, end_date="2026-09-03")
    assert result["top_category"] == "Bills", \
        f"Expected Bills as top category for Sep 01–03, got {result['top_category']}"


def test_get_summary_stats_empty_range(app):
    with app.app_context():
        result = queries.get_summary_stats(
            1, start_date="2025-01-01", end_date="2025-01-31"
        )
    assert result["total_spent"] == "₹0.00"
    assert result["transaction_count"] == 0
    assert result["top_category"] == "—"


def test_get_summary_stats_single_day_range(app):
    """Sep 06 has exactly one expense: Shopping ₹89.99."""
    with app.app_context():
        result = queries.get_summary_stats(
            1, start_date="2026-09-06", end_date="2026-09-06"
        )
    assert result["total_spent"] == "₹89.99", \
        f"Expected ₹89.99 for Sep 06 only, got {result['total_spent']}"
    assert result["transaction_count"] == 1
    assert result["top_category"] == "Shopping"


# ------------------------------------------------------------------ #
# get_category_breakdown with date params                             #
# ------------------------------------------------------------------ #

def test_get_category_breakdown_start_and_end_date_category_count(app):
    """Sep 01–05 contains 5 distinct categories."""
    with app.app_context():
        result = queries.get_category_breakdown(
            1, start_date="2026-09-01", end_date="2026-09-05"
        )
    names = [cat["name"] for cat in result]
    assert len(result) == 5, \
        f"Expected 5 categories for Sep 01–05, got {len(result)}: {names}"


def test_get_category_breakdown_start_and_end_date_top_category(app):
    with app.app_context():
        result = queries.get_category_breakdown(
            1, start_date="2026-09-01", end_date="2026-09-05"
        )
    assert result[0]["name"] == "Bills", \
        f"Expected Bills as top category for Sep 01–05, got {result[0]['name']}"
    assert result[0]["amount"] == "₹120.00"


def test_get_category_breakdown_start_and_end_date_percents_sum_to_100(app):
    with app.app_context():
        result = queries.get_category_breakdown(
            1, start_date="2026-09-01", end_date="2026-09-05"
        )
    total_pct = sum(cat["percent"] for cat in result)
    assert total_pct == 100, \
        f"Category percents should sum to exactly 100, got {total_pct}"


def test_get_category_breakdown_start_and_end_date_all_keys_present(app):
    with app.app_context():
        result = queries.get_category_breakdown(
            1, start_date="2026-09-01", end_date="2026-09-05"
        )
    for cat in result:
        assert set(cat.keys()) == {"name", "amount", "percent"}, \
            f"Unexpected keys in category breakdown entry: {set(cat.keys())}"


def test_get_category_breakdown_start_date_only_two_categories(app):
    """Sep 07 only: Food (₹22.00) and Other (₹15.75)."""
    with app.app_context():
        result = queries.get_category_breakdown(1, start_date="2026-09-07")
    assert len(result) == 2, \
        f"Expected 2 categories for Sep 07, got {len(result)}"
    assert result[0]["name"] == "Food", \
        f"Food should be top category on Sep 07, got {result[0]['name']}"
    assert result[0]["amount"] == "₹22.00"
    assert result[1]["name"] == "Other"
    assert result[1]["amount"] == "₹15.75"


def test_get_category_breakdown_start_date_only_percents_sum_to_100(app):
    with app.app_context():
        result = queries.get_category_breakdown(1, start_date="2026-09-07")
    total_pct = sum(cat["percent"] for cat in result)
    assert total_pct == 100, \
        f"Category percents should sum to 100 for Sep 07, got {total_pct}"


def test_get_category_breakdown_end_date_only_three_categories(app):
    """Sep 01–03: Food, Transport, Bills — exactly 3 categories."""
    with app.app_context():
        result = queries.get_category_breakdown(1, end_date="2026-09-03")
    names = [cat["name"] for cat in result]
    assert len(result) == 3, \
        f"Expected 3 categories for Sep 01–03, got {len(result)}: {names}"
    assert result[0]["name"] == "Bills", \
        f"Bills should be top category for Sep 01–03, got {result[0]['name']}"
    assert result[0]["amount"] == "₹120.00"


def test_get_category_breakdown_end_date_only_percents_sum_to_100(app):
    with app.app_context():
        result = queries.get_category_breakdown(1, end_date="2026-09-03")
    total_pct = sum(cat["percent"] for cat in result)
    assert total_pct == 100, \
        f"Category percents should sum to 100 for Sep 01–03, got {total_pct}"


def test_get_category_breakdown_empty_range_returns_empty_list(app):
    with app.app_context():
        result = queries.get_category_breakdown(
            1, start_date="2025-01-01", end_date="2025-01-31"
        )
    assert result == [], \
        "Expected empty list for a date range with no expenses"


def test_get_category_breakdown_shopping_only_single_category(app):
    """Sep 06 has only Shopping ₹89.99 — single category, 100%."""
    with app.app_context():
        result = queries.get_category_breakdown(
            1, start_date="2026-09-06", end_date="2026-09-06"
        )
    assert len(result) == 1, \
        f"Expected 1 category for Sep 06, got {len(result)}"
    assert result[0]["name"] == "Shopping"
    assert result[0]["amount"] == "₹89.99"
    assert result[0]["percent"] == 100
