from fintrack import add_expense, view_expenses, update_expense, delete_expense, search_expenses

# ─── Test 1: Add expenses ───
print("\n--- ADDING EXPENSES ---")
add_expense('2025-10-14', 'Food', 250.00, 'Lunch with friends')
add_expense('2025-10-13', 'Travel', 120.50, 'Cab to office')
add_expense('2025-10-12', 'Shopping', 950.00, 'New shoes')

# ─── Test 2: View all ───
print("\n--- VIEW ALL EXPENSES ---")
view_expenses()

# ─── Test 3: Search category ───
print("\n--- SEARCH CATEGORY: Food ---")
search_expenses('Food')

# ─── Test 4: Update one record (change amount or desc) ───
print("\n--- UPDATE RECORD ---")
update_expense(1, '2025-10-14', 'Food', 300.00, 'Updated lunch expense')

# ─── Test 5: Delete one record ───
print("\n--- DELETE RECORD ---")
delete_expense(2)

# ─── View again after delete ───
print("\n--- VIEW AFTER DELETE ---")
view_expenses()
