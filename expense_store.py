from datetime import date, datetime, timedelta
from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "expenses.db"


def _connect():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spent_on TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def _normalize_date(value):
    if isinstance(value, date):
        return value.isoformat()
    return datetime.strptime(value, "%Y-%m-%d").date().isoformat()


def add_expense(spent_on, category, description, amount):
    spent_on = _normalize_date(spent_on)
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO expenses (spent_on, category, description, amount)
            VALUES (?, ?, ?, ?)
            """,
            (spent_on, category, description, amount),
        )
        conn.commit()
        return cursor.lastrowid


def get_expense(expense_id):
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, spent_on, category, description, amount FROM expenses WHERE id = ?",
            (expense_id,),
        ).fetchone()
        return dict(row) if row else None


def update_expense(expense_id, spent_on, category, description, amount):
    spent_on = _normalize_date(spent_on)
    with _connect() as conn:
        conn.execute(
            """
            UPDATE expenses
            SET spent_on = ?, category = ?, description = ?, amount = ?
            WHERE id = ?
            """,
            (spent_on, category, description, amount, expense_id),
        )
        conn.commit()


def delete_expense(expense_id):
    with _connect() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()


def list_expenses(limit=None):
    query = "SELECT id, spent_on, category, description, amount FROM expenses ORDER BY spent_on DESC, id DESC"
    params = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (limit,)
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def list_expenses_for_day(day_value):
    spent_on = _normalize_date(day_value)
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, spent_on, category, description, amount
            FROM expenses
            WHERE spent_on = ?
            ORDER BY id DESC
            """,
            (spent_on,),
        ).fetchall()
        return [dict(row) for row in rows]


def _month_bounds(month_value):
    month_start = datetime.strptime(month_value, "%Y-%m").date().replace(day=1)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    return month_start.isoformat(), next_month.isoformat()


def monthly_report(month_value):
    start_date, end_date = _month_bounds(month_value)
    with _connect() as conn:
        total_row = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count
            FROM expenses
            WHERE spent_on >= ? AND spent_on < ?
            """,
            (start_date, end_date),
        ).fetchone()

        category_rows = conn.execute(
            """
            SELECT category, SUM(amount) AS total
            FROM expenses
            WHERE spent_on >= ? AND spent_on < ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (start_date, end_date),
        ).fetchall()

        daily_rows = conn.execute(
            """
            SELECT spent_on AS day, SUM(amount) AS total
            FROM expenses
            WHERE spent_on >= ? AND spent_on < ?
            GROUP BY spent_on
            ORDER BY spent_on
            """,
            (start_date, end_date),
        ).fetchall()

        top_category = conn.execute(
            """
            SELECT category, SUM(amount) AS total
            FROM expenses
            WHERE spent_on >= ? AND spent_on < ?
            GROUP BY category
            ORDER BY total DESC
            LIMIT 1
            """,
            (start_date, end_date),
        ).fetchone()

        top_day = conn.execute(
            """
            SELECT spent_on AS day, SUM(amount) AS total
            FROM expenses
            WHERE spent_on >= ? AND spent_on < ?
            GROUP BY spent_on
            ORDER BY total DESC
            LIMIT 1
            """,
            (start_date, end_date),
        ).fetchone()

        expense_rows = conn.execute(
            """
            SELECT id, spent_on, category, description, amount
            FROM expenses
            WHERE spent_on >= ? AND spent_on < ?
            ORDER BY spent_on DESC, id DESC
            """,
            (start_date, end_date),
        ).fetchall()

    total = float(total_row["total"] or 0)
    count = int(total_row["count"] or 0)
    average = total / count if count else 0

    return {
        "month": month_value,
        "start_date": start_date,
        "end_date": end_date,
        "total": total,
        "count": count,
        "average": average,
        "top_category": dict(top_category) if top_category else None,
        "top_day": dict(top_day) if top_day else None,
        "category_breakdown": [dict(row) for row in category_rows],
        "daily_breakdown": [dict(row) for row in daily_rows],
        "expenses": [dict(row) for row in expense_rows],
    }
