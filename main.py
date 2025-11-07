from fintrack import add_expense, view_expenses, update_expense, delete_expense, search_expenses
from fin_analytics import show_category_expense_chart, show_monthly_expense_chart
from datetime import datetime

def show_menu():
  print("\n" + "="*50)
  print("💸 FINTRACK - SMART EXPENSE MANAGER ")
  print("="*50)
  print("1️⃣  Add Expense")
  print("2️⃣  View All Expenses")
  print("3️⃣  Update Expense")
  print("4️⃣  Delete Expense")
  print("5️⃣  Search Expense (by category)")
  print("6️⃣  Show Analytics - Spending by Category (Pie Chart)")
  print("7️⃣  Show Analytics - Monthly Spending (Bar Chart)")
  print("0️⃣  Exit")
  print("-"*50)

def main():
  while True:
    show_menu()
    choice = input("👉 Enter your choice: ").strip()

    if choice == '1':
       date_str = input("Enter date (YYYY-MM-DD):")
       category = input("ENter category: ")
       amount = float(input("Enter amount: "))
       description = input("Enter description: ")
       add_expense(date_str, category, amount, description)

    elif choice == '2':
       view_expenses()

    elif choice == '3':
       expense_id = int(input("Enter Expense ID to update: "))
       date_str = input("Enter new date (YYYY-MM-DD):")
       category = input("Enter new category: ")    
       amount = float(input("Enter new amount: "))
       description = input("Enter new description: ")
       update_expense(expense_id, date_str, category, amount, description)

    elif choice == '4':
       expense_id = int(input("ENter Expense ID to delete: "))  
       delete_expense(expense_id)

    elif choice == '5':
       category = input("Enter category to search: ")
       search_expenses(category)

    elif choice == '6':
        show_category_expense_chart()

    elif choice == '7':
        show_monthly_expense_chart()

    elif choice == '0':
       print("\n👋 Exiting FinTrack. Goodbye!")

    else: 
       print("⚠️ Invalid choice! Please try again.")  

if __name__ == "__main__":
   main()