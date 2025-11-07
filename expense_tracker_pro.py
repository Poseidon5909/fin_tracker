import csv
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

FILENAME = 'expenses.csv'
DATE_FORMAT = "%Y-%m-%d"

# Initialize CSV file
def init_file():
    if not os.path.exists(FILENAME):
        with open(FILENAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Amount", "Description"])


# Add new expense
def add_expense():
    date = input(f"Enter date ({DATE_FORMAT}) or leave blank for today: ").strip()
    if not date:
        date = datetime.now().strftime(DATE_FORMAT)
    category = input("Enter category (Food, Travel, Bills, etc.): ").strip().title() or "Misc"
    amount = float(input("Enter amount: "))
    description = input("Enter short description: ").strip()

    with open(FILENAME, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, category, amount, description])
    print("✅ Expense added successfully!")


# View all expenses in table form
def view_expenses():
  try:
    df = pd.read_csv(FILENAME, parse_dates=["Date"])
    if df.empty:
      print("⚠️ No expenses found!")
      return
    print("\n📋 All Expenses:\n")
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))
  except FileNotFoundError:
    print("⚠️ File not found!")

# Monthly summary + trend chart
def monthly_summary():
    df = pd.read_csv(FILENAME, parse_dates=["Date"])
    if df.empty:
        print("⚠️ No data yet!")
        return
    df["YearMonth"] = df["Date"].dt.to_period("M")
    monthly_totals = df.groupby("YearMonth")["Amount"].sum()
    print("\n📅 Monthly Spending Summary:\n")
    print(tabulate(monthly_totals.reset_index(), headers=["Month", "Total (₹)"], tablefmt="grid"))

    # Chart
    monthly_totals.plot(kind="line", marker="o", title="Monthly Spending Trend", ylabel="Amount (₹)", xlabel="Month")
    plt.tight_layout()
    plt.show()


# Category comparison chart
def category_summary():
    df = pd.read_csv(FILENAME, parse_dates=["Date"])
    if df.empty:
        print("⚠️ No data found!")
        return
    totals = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    print("\n📊 Total Spending by Category:\n")
    print(tabulate(totals.reset_index(), headers=["Category", "Total (₹)"], tablefmt="grid"))

    totals.plot(kind="bar", title="Spending by Category", xlabel="Category", ylabel="Amount (₹)")
    plt.tight_layout()
    plt.show()


# Export report to PDF
def export_pdf_report():
    df = pd.read_csv(FILENAME, parse_dates=["Date"])
    if df.empty:
        print("⚠️ No expenses to export!")
        return

    total_spent = df["Amount"].sum()
    top_category = df.groupby("Category")["Amount"].sum().idxmax()
    filename = "Expense_Report.pdf"

    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, 800, "Expense Report")

    c.setFont("Helvetica", 12)
    c.drawString(100, 760, f"Total Expenses: ₹{total_spent:.2f}")
    c.drawString(100, 740, f"Top Category: {top_category}")

    c.drawString(100, 710, "Recent Transactions:")
    y = 690
    for _, row in df.tail(10).iterrows():
        c.drawString(100, y, f"{row['Date'].strftime('%Y-%m-%d')} | {row['Category']:<10} | ₹{row['Amount']:<8.2f} | {row['Description']}")
        y -= 15
        if y < 100:
            c.showPage()
            y = 750

    c.save()
    print(f"✅ PDF report saved as '{filename}'")


# Main menu
def main():
    init_file()
    while True:
        print("\n------ Expense Tracker (Advanced Analytics) ------")
        print("1️⃣  Add Expense")
        print("2️⃣  View All Expenses")
        print("3️⃣  Monthly Summary + Trend Chart")
        print("4️⃣  Category Summary + Chart")
        print("5️⃣  Export PDF Report")
        print("6️⃣  Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            monthly_summary()
        elif choice == "4":
            category_summary()
        elif choice == "5":
            export_pdf_report()
        elif choice == "6":
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")


if __name__ == "__main__":
    main()


