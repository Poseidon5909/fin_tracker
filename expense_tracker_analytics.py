import csv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os

FILENAME = "expense.csv"
DATE_FORMAT = "%Y-%m-%d"

def init_file():
  if not os.path.exists(FILENAME):
    with open(FILENAME, 'w', newline='') as f:
      writer = csv.writer(f)
      writer.writerow(["Date", "Category", "Amount", "Description"])

def parse_date_input(prompt):
  while True:
    s = input(prompt + f" (format: {DATE_FORMAT}) [leave blank for today]: ").strip()
    if not s:
      return datetime.now().strftime(DATE_FORMAT)
    try:
      dt = datetime.strptime(s, DATE_FORMAT)
      return dt.strftime(DATE_FORMAT)
    except ValueError:
      print(f"❌ Invalid date. Please use format {DATE_FORMAT} (e.g. 2025-10-13).")

def add_expense():
  date = parse_date_input("Enter date")
  category = input("Enter category (Food, Travel, Bills, etc.): ").strip() or "Misc"
  while True:
    amt_s = input("Enter amount spent: ").strip()
    try:
      amount = float(amt_s)
      break
    except ValueError:
      print("❌ Invalid amount. Enter a number (e.g. 250 or 99.50).")
  description = input("Enter short description (optional):").strip()

  with open(FILENAME, 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([date, category, amount, description])
  print("✅ Expense added successfully!")

def view_expense(limit=None):
    try:
        df = pd.read_csv(FILENAME, parse_dates=["Date"])
        if df.empty:
            print("⚠️ No expenses found.")
            return
        df = df.sort_values("Date", ascending=False)
        if limit:
            df = df.head(limit)

        print("\n--- Recent Expenses ---")
        table_str = df.to_string(index=False, justify="left")

        print("\n".join(line.rstrip() for line in table_str.splitlines()))
    except FileNotFoundError:
        print("⚠️ No expenses found. Add some first.")

def view_expenses(limit=None):
    """Compatibility wrapper: call the singular view_expense function.

    The main menu expects `view_expenses`. Reuse `view_expense` to avoid
    duplicating logic.
    """
    return view_expense(limit=limit)
def total_by_category():
   try:
      df = pd.read_csv(FILENAME, parse_dates=["Date"])
      totals = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
      print("\n📊 Total spending by category:")
      print(totals.to_string())
   except FileNotFoundError:
      print("⚠️ No expenses found!")

def monthly_summary():
   try:
      df = pd.read_csv(FILENAME, parse_dates=["Date"])
      if df.empty:
         print("⚠️ No expenses found.")
         return
      df['YearMonth'] = df['Date'].dt.to_period('M')
      summary = df.groupby('YearMonth')['Amount'].sum().sort_index()
      print("\n📅 Monthly spending:")
      print(summary.to_string())
   except  FileNotFoundError:
      print("⚠️ No expenses found!")

def plot_category_for_month():
   try:
      df = pd.read_csv(FILENAME, parse_dates=["Date"])
      if df.empty:
         print("⚠️ No expenses found.")
         return
      df['YearMonth'] = df['Date'].dt.to_period('M')
      #Ask for Month
      month_input = input("Enter month to plot (YYY-MM) or leave blank for latest: ").strip()
      if month_input: 
          try:
             ym = pd.Period(month_input, freq='M')
          except Exception:
             print("❌ Invalid month format. Use YYYY-MM (e.g. 2025-10).")
             return
      else:
         ym = df['YearMonth'].mac()

      df_month = df[df['YearMonth'] == ym]
      if df_month.empty:
            print(f"⚠️ No data for {ym}.")
            return

      cat_totals = df_month.groupby('Category')['Amount'].sum().sort_values(ascending=False)

      print(f"\n🎯 Spending by category for {ym}:")
      print(cat_totals.to_string()) 

       # Plot
      plt.figure(figsize=(8,5))
      cat_totals.plot(kind='bar')
      plt.title(f"Spending by Category — {ym}")
      plt.ylabel("Amount")
      plt.xlabel("Category")
      plt.tight_layout()
      plt.show()
   except FileNotFoundError:
    print("⚠️ No expenses found!")

def export_month_report():
    try:
        df = pd.read_csv(FILENAME, parse_dates=["Date"])
        if df.empty:
            print("⚠️ No expenses found.")
            return
        df['YearMonth'] = df['Date'].dt.to_period('M')

        while True:
          month_input = input("Enter month to export (YYYY-MM) or leave blank for latest: ").strip()
          if not month_input:
             ym = df['YearMonth'].max()
             break
          try:
             ym = pd.Period(month_input, freq='M')
             break
          except Exception:
             print("❌ Invalid month format. Please use **YYYY-MM** (e.g. 2025-01 or 2025-10).")
             continue
          
        df_month = df[df['YearMonth'] == ym]
        if df_month.empty:
            print(f"⚠️ No data for {ym}.")
            return
        out_name = f"expense_report_{ym}.csv"
        df_month.to_csv(out_name, index=False)
        print(f"✅ Exported {out_name}")
    except FileNotFoundError:
        print("⚠️ No expenses found!") 

def main():
    init_file()
    while True:
        print("\n----- Expense Tracker (Analytics) -----")
        print("1. Add Expense")
        print("2. View Recent Expenses")
        print("3. View Total by Category")
        print("4. Monthly Summary")
        print("5. Plot category spending for a month")
        print("6. Export month report (CSV)")
        print("7. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses(limit=20)
        elif choice == "3":
            total_by_category()
        elif choice == "4":
            monthly_summary()
        elif choice == "5":
            plot_category_for_month()
        elif choice == "6":
            export_month_report()
        elif choice == "7":
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again.")

if __name__ == "__main__":
    main()
    