import matplotlib.pyplot as plt
from db.db.db_connect import get_connection


def category_chart(file_path="category_chart.png"):
    """Generate a pie chart of expenses by category."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT category, SUM(amount) 
            FROM fin_expenses 
            GROUP BY category 
            ORDER BY SUM(amount) DESC;
        """)
        data = cur.fetchall()
        cur.close()
        conn.close()

        if not data:
            print("⚠️ No expense data available for category chart.")
            return None

        categories = [row[0] for row in data]
        amounts = [row[1] for row in data]

        plt.figure(figsize=(6, 6))
        plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
        plt.title("Expenses by Category", fontsize=14, fontweight="bold")
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()
        print(f"✅ Category chart saved to {file_path}")
        return file_path
    except Exception as e:
        print("❌ Error generating category chart:", e)
        return None


def monthly_chart(file_path="monthly_chart.png"):
    """Generate a bar chart of monthly total expenses."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT TO_CHAR(date, 'YYYY-MM') AS month, SUM(amount)
            FROM fin_expenses
            GROUP BY month
            ORDER BY month;
        """)
        data = cur.fetchall()
        cur.close()
        conn.close()

        if not data:
            print("⚠️ No expense data available for monthly chart.")
            return None

        months = [row[0] for row in data]
        totals = [row[1] for row in data]

        plt.figure(figsize=(8, 5))
        plt.bar(months, totals)
        plt.title("Monthly Expense Trend", fontsize=14, fontweight="bold")
        plt.xlabel("Month")
        plt.ylabel("Total Amount (₹)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()
        print(f"✅ Monthly chart saved to {file_path}")
        return file_path
    except Exception as e:
        print("❌ Error generating monthly chart:", e)
        return None
