import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import csv

FILENAME = "expenses.csv"
DATE_FORMAT = "%Y-%m-%d" 

# --- Global Widget Variables ---

root = tk.Tk()
date_entry = tk.Entry(root)
category_entry = tk.Entry(root)
amount_entry = tk.Entry(root)
desc_entry = tk.Entry(root)
tree = ttk.Treeview(root)
total_label = tk.Label(root) 

# --- File Management ---

def init_file():
    """Ensures the CSV file exists with the header."""
    if not os.path.exists(FILENAME):
        with open(FILENAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Amount", "Description"])

def total_spent():
    """Calculates and returns the total spending from the CSV file."""
    if not os.path.exists(FILENAME) or os.path.getsize(FILENAME) == 0:
        return 0.0
    try:
        df = pd.read_csv(FILENAME)
        return df["Amount"].sum() if not df.empty else 0.0
    except pd.errors.EmptyDataError:
        return 0.0
    except Exception:
        # Handle cases where the file might be corrupt or unreadable
        return 0.0

# --- Data Display and Utility ---

def load_data():
    """Loads data from the CSV file and updates the Treeview and Total Spent label."""
    global total_label
    

    for row in tree.get_children():
        tree.delete(row)

    if not os.path.exists(FILENAME):

        total_label.config(text=f"💰 Total Spent: ₹{0.00:.2f}")
        return

  
    try:
        df = pd.read_csv(FILENAME)
        for _, row in df.iterrows():
          
            tree.insert("", "end", values=(row["Date"], row["Category"], f"₹{row['Amount']:,.2f}", row["Description"]))
            
        total_spent_amount = df["Amount"].sum() if not df.empty else 0.0
        total_label.config(text=f"💰 Total Spent: ₹{total_spent_amount:,.2f}")
        
    except pd.errors.EmptyDataError:
        total_label.config(text=f"💰 Total Spent: ₹{0.00:.2f}")

def clear_entries():
    """Clears input fields and sets the date back to today."""
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    date_entry.insert(0, datetime.now().strftime(DATE_FORMAT))

# --- Expense Logic ---

def add_expense():
    """Validates input, adds expense to the file, and refreshes the GUI."""
    date_input = date_entry.get().strip()
    category = category_entry.get().strip().title()
    description = desc_entry.get().strip()
    amount_str = amount_entry.get().strip()

    if not amount_str or not category:
        messagebox.showerror("Error", "Category and Amount are required!")
        return

    # Amount Validation
    try:
        amount = float(amount_str)
        if amount <= 0:
            messagebox.showerror("Error", "Amount must be a positive number!")
            return
    except ValueError:
        messagebox.showerror("Error", "Enter a valid numerical amount!")
        return

    if not date_input:
        date = datetime.now().strftime(DATE_FORMAT)
    else:
        try:
            datetime.strptime(date_input, DATE_FORMAT)
            date = date_input
        except ValueError:
            messagebox.showerror("Error", f"Invalid date format. Please use: {DATE_FORMAT}")
            return

    # Write to file
    with open(FILENAME, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, category, amount, description])

    messagebox.showinfo("Success", "Expense added successfully!")
    load_data()
    clear_entries()

def delete_expense():
    """Deletes the selected row from the Treeview and the CSV file."""
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror("Error", "Please select an expense to delete.")
        return

    # Get the values of the selected row
    values = tree.item(selected_item, 'values')
    
    if not values:
        return

    # Extract clean data for matching (remove '₹' and convert amount)
    try:
        date_to_match = values[0]
        category_to_match = values[1]
        amount_to_match = float(values[2].replace('₹', '').replace(',', '')) 
        description_to_match = values[3]
    except ValueError:
        messagebox.showerror("Error", "Could not parse selected expense data for deletion.")
        return

    # Confirmation box
    if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the expense for {date_to_match} in {category_to_match}?"):
        return

    try:
        df = pd.read_csv(FILENAME)
      
        mask = (df['Date'] == date_to_match) & \
               (df['Category'] == category_to_match) & \
               (df['Amount'].round(2) == round(amount_to_match, 2)) & \
               (df['Description'] == description_to_match)

        indices_to_drop = df[mask].index

        if not indices_to_drop.empty:
            df.drop(indices_to_drop[0], inplace=True)
            df.to_csv(FILENAME, index=False)
            
            messagebox.showinfo("Success", "Expense deleted successfully!")
            load_data()
        else:
             messagebox.showerror("Error", "Matching entry not found in file.")

    except FileNotFoundError:
        messagebox.showerror("Error", "Expense file not found!")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred during deletion: {e}")    

def show_chart():
    """Displays a bar chart of spending by category."""
    if not os.path.exists(FILENAME):
        messagebox.showerror("Error", "No data available!")
        return

    try:
        df = pd.read_csv(FILENAME)
        if df.empty:
            messagebox.showinfo("Info", "No data found!")
            return

        totals = df.groupby("Category")["Amount"].sum()
        
        plt.figure(figsize=(6, 4))
        totals.plot(kind="bar", color="skyblue")
        plt.title("Spending by Category")
        plt.xlabel("Category")
        plt.ylabel("Total Amount (₹)")
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Chart Error", f"Could not generate chart: {e}")

# --- GUI Setup ---

def create_widgets():
    global date_entry, category_entry, amount_entry, desc_entry, tree, total_label
    
    root.title("Expense Tracker (Tkinter Edition)")
    root.geometry("750x500")
    root.resizable(False, False)

    # --- Input frame ---
    frame = tk.LabelFrame(root, text="Add New Expense", padx=10, pady=10)
    frame.pack(fill="x", padx=10, pady=10)

    # Date Entry
    tk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
    date_entry = tk.Entry(frame, width=15)
    date_entry.grid(row=0, column=1, padx=5, pady=5)
    date_entry.insert(0, datetime.now().strftime(DATE_FORMAT)) # Pre-populate date (FIXED GUI)

    # Category Entry
    tk.Label(frame, text="Category:").grid(row=0, column=2, padx=5, pady=5)
    category_entry = tk.Entry(frame, width=15)
    category_entry.grid(row=0, column=3, padx=5, pady=5)

    # Amount Entry
    tk.Label(frame, text="Amount (₹):").grid(row=1, column=0, padx=5, pady=5)
    amount_entry = tk.Entry(frame, width=15)
    amount_entry.grid(row=1, column=1, padx=5, pady=5)

    # Description Entry
    tk.Label(frame, text="Description:").grid(row=1, column=2, padx=5, pady=5)
    desc_entry = tk.Entry(frame, width=20)
    desc_entry.grid(row=1, column=3, padx=5, pady=5)

    # Add Button
    tk.Button(frame, text="Add Expense", command=add_expense, bg="#4CAF50", fg="white").grid(row=2, column=3, pady=10)

    # --- Expense Table ---
    columns = ("Date", "Category", "Amount", "Description")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Summary + Buttons ---
    summary_frame = tk.Frame(root)
    summary_frame.pack(pady=5)

    tk.Button(summary_frame, text="Show Category Chart", command=show_chart, bg="#2196F3", fg="white").grid(row=0, column=0, padx=10)
    tk.Button(summary_frame, text="Refresh Data", command=load_data, bg="#9C27B0", fg="white").grid(row=0, column=1, padx=10)
    tk.Button(summary_frame, text="🗑️ Delete Selected", command=delete_expense, bg="#F44336", fg="white").grid(row=0, column=2, padx=10)
    
    # Initialize the total_label
    total_label = tk.Label(summary_frame, text="💰 Total Spent: ₹0.00", font=("Arial", 12, "bold"))
    total_label.grid(row=0, column=3, padx=10)

# --- Main Execution ---

if __name__ == "__main__":
    init_file()
    create_widgets()
    load_data()
    root.mainloop()