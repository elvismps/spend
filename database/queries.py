from datetime import datetime
from database.db import get_db


def _date_where(start_date, end_date):
    parts, params = [], []
    if start_date:
        parts.append("date >= ?")
        params.append(start_date)
    if end_date:
        parts.append("date <= ?")
        params.append(end_date)
    sql = (" AND " + " AND ".join(parts)) if parts else ""
    return sql, params


def get_user_by_id(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT name, email, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    name = row["name"]
    member_since = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S").strftime("%B %Y")
    initials = "".join(w[0].upper() for w in name.split())[:2]
    return {
        "name":         name,
        "email":        row["email"],
        "member_since": member_since,
        "initials":     initials,
    }


def get_recent_transactions(user_id, limit=10, start_date=None, end_date=None):
    date_sql, date_params = _date_where(start_date, end_date)
    sql = (
        "SELECT date, description, category, amount"
        " FROM expenses WHERE user_id = ?" + date_sql +
        " ORDER BY date DESC, id DESC"
    )
    params = [user_id] + date_params
    if not date_sql:
        sql += " LIMIT ?"
        params.append(limit)
    conn = get_db()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            "date":        datetime.strptime(row["date"], "%Y-%m-%d").strftime("%d %b %Y"),
            "description": row["description"],
            "category":    row["category"],
            "amount":      f"₹{row['amount']:,.2f}",
        })
    return result


def get_summary_stats(user_id, start_date=None, end_date=None):
    date_sql, date_params = _date_where(start_date, end_date)
    conn = get_db()
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0.0) AS total_spent, COUNT(*) AS transaction_count"
        " FROM expenses WHERE user_id = ?" + date_sql,
        [user_id] + date_params,
    ).fetchone()
    total_spent = row["total_spent"]
    count = int(row["transaction_count"])
    if count == 0:
        top_category = "—"
    else:
        cat_row = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ?" + date_sql +
            " GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            [user_id] + date_params,
        ).fetchone()
        top_category = cat_row["category"] if cat_row else "—"
    conn.close()
    return {
        "total_spent":       f"₹{total_spent:,.2f}",
        "transaction_count": count,
        "top_category":      top_category,
    }


def get_category_breakdown(user_id, start_date=None, end_date=None):
    date_sql, date_params = _date_where(start_date, end_date)
    conn = get_db()
    rows = conn.execute(
        "SELECT category, SUM(amount) AS total FROM expenses"
        " WHERE user_id = ?" + date_sql + " GROUP BY category ORDER BY total DESC",
        [user_id] + date_params,
    ).fetchall()
    conn.close()
    if not rows:
        return []
    grand_total = sum(row["total"] for row in rows)
    if grand_total == 0:
        return []
    floors = [int(row["total"] / grand_total * 100) for row in rows]
    floors[0] += 100 - sum(floors)
    return [
        {
            "name":    row["category"],
            "amount":  f"₹{row['total']:,.2f}",
            "percent": floors[i],
        }
        for i, row in enumerate(rows)
    ]
