from datetime import date, datetime
import calendar
import os

from flask import Flask, flash, redirect, render_template, request, url_for

from expense_store import (
    add_expense,
    delete_expense,
    get_expense,
    init_db,
    list_expenses,
    list_expenses_for_day,
    monthly_report,
    update_expense,
)


app = Flask(__name__)
app.secret_key = os.getenv("FIN_TRACK_SECRET", "dev-secret-key-change-in-production")
app.config["ENV"] = os.getenv("FLASK_ENV", "development")
app.config["DEBUG"] = app.config["ENV"] == "development"

CATEGORIES = ["Food", "Travel", "Bills", "Shopping", "Health", "Entertainment", "Other"]


def month_options(back_months=6):
    today = date.today().replace(day=1)
    options = []
    for offset in range(back_months):
        year = today.year
        month = today.month - offset
        while month <= 0:
            month += 12
            year -= 1
        options.append(f"{year:04d}-{month:02d}")
    return options


def current_month_value():
    return date.today().strftime("%Y-%m")


def current_day_value():
    return date.today().isoformat()


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


@app.before_request
def ensure_database():
    init_db()


@app.route("/", methods=["GET", "POST"])
def dashboard():
    selected_month = request.args.get("month", current_month_value())
    selected_day = request.args.get("day", current_day_value())

    if request.method == "POST":
        spent_on = request.form.get("spent_on", current_day_value()).strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        amount_text = request.form.get("amount", "").strip()

        if not spent_on or not category or not description or not amount_text:
            flash("All expense fields are required.", "error")
            return redirect(url_for("dashboard", month=spent_on[:7] if spent_on else selected_month, day=spent_on or selected_day))

        try:
            parse_date(spent_on)
            amount = float(amount_text)
        except ValueError:
            flash("Enter a valid date and amount.", "error")
            return redirect(url_for("dashboard", month=selected_month, day=selected_day))

        add_expense(spent_on, category, description, amount)
        flash("Expense saved.", "success")
        return redirect(url_for("dashboard", month=spent_on[:7], day=spent_on))

    monthly = monthly_report(selected_month)
    today_expenses = list_expenses_for_day(selected_day)
    recent_expenses = list_expenses(limit=8)

    return render_template(
        "index.html",
        categories=CATEGORIES,
        selected_month=selected_month,
        selected_day=selected_day,
        month_options=month_options(),
        monthly=monthly,
        today_expenses=today_expenses,
        recent_expenses=recent_expenses,
        current_day=current_day_value(),
    )


@app.route("/report")
def report():
    selected_month = request.args.get("month", current_month_value())
    monthly = monthly_report(selected_month)
    return render_template(
        "report.html",
        monthly=monthly,
        selected_month=selected_month,
        month_options=month_options(12),
    )


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    expense = get_expense(expense_id)
    if expense is None:
        flash("Expense not found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        spent_on = request.form.get("spent_on", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        amount_text = request.form.get("amount", "").strip()

        if not spent_on or not category or not description or not amount_text:
            flash("All fields are required.", "error")
        else:
            try:
                parse_date(spent_on)
                amount = float(amount_text)
                update_expense(expense_id, spent_on, category, description, amount)
                flash("Expense updated.", "success")
                return redirect(url_for("report", month=spent_on[:7]))
            except ValueError:
                flash("Enter a valid date and amount.", "error")

    return render_template("edit.html", expense=expense, categories=CATEGORIES)


@app.post("/delete/<int:expense_id>")
def remove_expense(expense_id):
    expense = get_expense(expense_id)
    if expense is None:
        flash("Expense not found.", "error")
        return redirect(url_for("dashboard"))

    delete_expense(expense_id)
    flash("Expense deleted.", "success")
    return redirect(url_for("dashboard", month=expense["spent_on"][:7], day=expense["spent_on"]))


if __name__ == "__main__":
    app.run(debug=True)
