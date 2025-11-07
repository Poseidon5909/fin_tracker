import csv
from datetime import datetime

FILENAME = "expense.csv"

# Function to initialize file
def init_file():
  try:
    with open(FILENAME, 'x', newline='') as file:
      writer = csv.writer(file)
      writer.writerow(["Date", "Category", "Amount", "Description"])
  except FileExistsError:
    pass    #File already exists

# Function to add expense
def add_expense():
  date = datetime.now().strftime("%Y-%m-%d")
  category = input("Enter category (Food, Travel, Bills, etc.): ")
  amount = float(input("Enter amount spent: "))
  description = input("Enter short description: ")

  with open(FILENAME, 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([date, category, amount, description])

  print("✅ Expense added successfully!")

#Function to view all expenses
def view_expenses()  :
  try:
    with open(FILENAME, 'r') as file:
      reader = csv.reader(file)
      for row in reader:
        print(row)
  except FileNotFoundError:
    print("⚠️ No expenses found! Add some first.")


#Function to show total spending by category
def total_by_category():
  totals = {}
  try:
    with open(FILENAME, 'r') as file:
      reader = csv.DictReader(file)
      for row in reader:
        category = row["Category"]
        amount = float(row["Amount"])
        totals[category] = totals.get(category, 0) + amount

    print("\n📊 Total spending by category:")
    for cat, total in totals.items():
      print(f"  {cat}: ₹{total:.2f}")
  except FileNotFoundError:
    print("⚠️ No expenses found!")


# Main menu
def main():
  init_file()
  while True:
    print("\n----- Expwnse tracker -----")
    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. View Total by Category")
    print("4. Exit")

    choice = input("Enter your chioce: ")

    if choice == "1":
      add_expense()
    elif choice == "2":
      view_expenses()
    elif choice == "3"  :
      total_by_category()
    elif choice =="4":
      print("👋 Exiting... Goodbye!")
      break
    else:
      print("❌ Invalid choice, please try again.")


if __name__ == "__main__":
  main()


