import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import csv

FILENAME = "expenses.csv"
DATE_FORMAT = "%Y-%m-%d"

# --- Ensure file exists ---
def init_file():
    if not os.path.exists(FILENAME):
        with open(FILENAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Amount", "Description"])

# --- Load CSV ---
def load_data():
    if not os.path.exists(FILENAME):
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])
    return pd.read_csv(FILENAME)

# --- Save CSV ---
def save_data(df):
    df.to_csv(FILENAME, index=False)

# --- Refresh Table ---
def refresh_table(filtered_df=None):
    for row in tree.get_children():
        tree.delete(row)

    df = filtered_df if filtered_df is not None else load_data()
    for _, row in df.iterrows():
        tree.insert("", "end", values=(row["Date"], row["Category"], row["Amount"], row["Description"]))

    update_total(df)

# --- Add Expense ---
def add_expense():
    date = date_entry.get() or datetime.now().strftime(DATE_FORMAT)
    category = category_combo.get().strip().title()
    description = desc_entry.get().strip()
    amount = amount_entry.get().strip()

    if not amount or not category:
        messagebox.showerror("Error", "Category and Amount are required!")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Enter a valid amount!")
        return

    df = load_data()
    df.loc[len(df)] = [date, category, amount, description]
    save_data(df)

    clear_entries()
    refresh_table()

# --- Delete Selected ---
def delete_expense():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select an expense to delete!")
        return

    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?")
    if not confirm:
        return

    df = load_data()
    values = tree.item(selected[0], "values")
    df = df[~((df["Date"] == values[0]) & (df["Category"] == values[1]) & 
              (df["Amount"] == float(values[2])) & (df["Description"] == values[3]))]
    save_data(df)
    refresh_table()

def delete_by_values(values):
    """
    Deletes an expense row based on its values (used for the Edit function).
    Does NOT show a confirmation box.
    """
    if not values:
        return False
        
    try:
        df = load_data()
        
        date_to_match = values[0]
        category_to_match = values[1]
        amount_to_match = float(values[2]) # Already a float from treeview, no need for complex cleanup
        description_to_match = values[3]

        # Create a mask to identify the row
        mask = (df["Date"] == date_to_match) & \
               (df["Category"] == category_to_match) & \
               (df["Amount"].round(2) == round(amount_to_match, 2)) & \
               (df["Description"] == description_to_match)
        
        indices_to_drop = df[mask].index
        
        if not indices_to_drop.empty:
            df.drop(indices_to_drop[0], inplace=True)
            save_data(df)
            return True
        return False

    except Exception as e:
        # Handle exceptions silently or log them, as this is a background helper
        print(f"Error in delete_by_values: {e}")
        return False

# --- Edit Selected ---
def edit_expense():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select an expense to edit!")
        return

    values = tree.item(selected[0], "values")

    date_entry.delete(0, tk.END)
    date_entry.insert(0, values[0])
    desc_entry.delete(0, tk.END)

    date_entry.insert(0, values[0])
    category_combo.set(values[1])

    amount_entry.insert(0, values[2])
    desc_entry.insert(0, values[3])

    if delete_by_values(values):
        refresh_table()
        messagebox.showinfo("Edit Mode", "Record loaded for editing. Click 'Add' to save changes.")
    else:
        messagebox.showerror("Error", "Could npt delete old record for editing.")    

    delete_expense()

# --- Search / Filter ---
def search_expenses():
    df = load_data()
    cat = search_category.get().strip().title()
    if cat:
        df = df[df["Category"] == cat]
    refresh_table(df)

# --- Show Chart ---
def show_chart():
    df = load_data()
    if df.empty:
        messagebox.showinfo("Info", "No data found!")
        return

    totals = df.groupby("Category")["Amount"].sum()
    plt.figure(figsize=(6, 4))
    totals.plot(kind="bar", color="teal")
    plt.title("Spending by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (₹)")
    plt.tight_layout()
    plt.show()

# --- Helpers ---
def clear_entries():
    date_entry.delete(0, tk.END)
    category_combo.set("")
    amount_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)

def update_total(df=None):
    if df is None:
        df = load_data()
    total = df["Amount"].sum() if not df.empty else 0
    total_label.config(text=f"💰 Total Spent: ₹{total:.2f}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Expense Tracker - Advanced GUI Edition")
root.geometry("850x600")
root.resizable(False, False)

init_file()

# --- Input Frame ---
frame = tk.LabelFrame(root, text="Add / Edit Expense", padx=10, pady=10)
frame.pack(fill="x", padx=10, pady=10)

tk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0)
date_entry = tk.Entry(frame, width=15)
date_entry.grid(row=0, column=1, padx=5)

tk.Label(frame, text="Category:").grid(row=0, column=2)
category_combo = ttk.Combobox(frame, values=["Food", "Travel", "Shopping", "Bills", "Other"], width=17)
category_combo.grid(row=0, column=3, padx=5)

tk.Label(frame, text="Amount (₹):").grid(row=1, column=0)
amount_entry = tk.Entry(frame, width=15)
amount_entry.grid(row=1, column=1, padx=5)

tk.Label(frame, text="Description:").grid(row=1, column=2)
desc_entry = tk.Entry(frame, width=20)
desc_entry.grid(row=1, column=3, padx=5)

tk.Button(frame, text="Add", command=add_expense, bg="#4CAF50", fg="white").grid(row=2, column=3, pady=5)
tk.Button(frame, text="Clear", command=clear_entries, bg="#757575", fg="white").grid(row=2, column=2, pady=5)

# --- Table ---
columns = ("Date", "Category", "Amount", "Description")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=180, anchor="center")

tree.pack(fill="both", expand=True, padx=10, pady=10)

# --- Search + Buttons ---
search_frame = tk.Frame(root)
search_frame.pack(pady=5)

search_category = tk.Entry(search_frame, width=20)
search_category.grid(row=0, column=0, padx=5)
tk.Button(search_frame, text="Search by Category", command=search_expenses, bg="#2196F3", fg="white").grid(row=0, column=1, padx=5)
tk.Button(search_frame, text="Show Chart", command=show_chart, bg="#00BCD4", fg="white").grid(row=0, column=2, padx=5)
tk.Button(search_frame, text="Edit Selected", command=edit_expense, bg="#FF9800", fg="white").grid(row=0, column=3, padx=5)
tk.Button(search_frame, text="Delete Selected", command=delete_expense, bg="#F44336", fg="white").grid(row=0, column=4, padx=5)
tk.Button(search_frame, text="Refresh", command=lambda: refresh_table(), bg="#9C27B0", fg="white").grid(row=0, column=5, padx=5)

total_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
total_label.pack(pady=5)

refresh_table()
root.mainloop()
