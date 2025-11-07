from db.db.db_connect import get_connection
from datetime import datetime

# Add New Expense
def add_expense(date, category, amount, description):
  conn = get_connection()
  if conn is None:
    return
  
  try:
      cursor = conn.cursor()
      query = """  INSERT INTO fin_expenses (date, category, amount, description)
            VALUES (%s, %s, %s, %s); """
      cursor.execute(query, (date, category, amount, description))
      conn.commit()
      print("✅ Expense added successfully.")
  except Exception as e:
      print("❌ Error adding expense:", e)
  finally:
      conn.close()  

# View All Expenses
def view_expenses():
  conn = get_connection()
  if conn is None:
    return
  
  try:
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM fin_expenses ORDER BY date DESC")
      records = cursor.fetchall()
      print("\n🧾 All Expenses:")
      for row in records:
        print(row)
  except Exception as e:
      print("❌ Error retrieving expenses:", e)
  finally:
      conn.close()

# Update Expense
def update_expense(expense_id, date, category, amount, description):
  conn = get_connection()
  if conn is None:
    return

  try:
      cursor = conn.cursor() 
      query = """
          UPDATE fin_expenses
          SET date=%s, category=%s, amount=%s, description=%s
          WHERE id=%s;
          """
      cursor.execute(query, (date, category, amount, description, expense_id))
      conn.commit()
      print("✅ Expense updated successfully.")
  except Exception as e:
      print("❌ Error updating expense:", e)
  finally:
     conn.close()

# Delete Expense
def delete_expense(expense_id):
   conn = get_connection()
   if conn is None:
      return
   
   try:
       cursor = conn.cursor()
       cursor.execute("DELETE FROM fin_expenses WHERE id=%s;", (expense_id,))
       conn.commit()
       print("🗑️ Expense deleted successfully.")
   except Exception as e:
       print("❌ Error deleting expense:", e)
   finally:
      conn.close()

# Search Expenses (By Category)
def search_expenses(category):
   conn = get_connection()
   if conn is None:
      return

   try:
       cursor = conn.cursor()
       cursor.execute("SELECT* FROM fin_expenses WHERE category ILIKE %s;", ('%' + category + '%',))
       records = cursor.fetchall()
       print(f"\n🔍 Expenses in category '{category}':")
       for row in records:
          print(row)
   except Exception as e:
      print("❌ Error searching expenses:", e)
   finally:
      conn.close()      