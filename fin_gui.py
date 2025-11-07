import ttkbootstrap as tb
from ttkbootstrap.style import Style
from tkinter import ttk, LEFT, RIGHT, TOP, BOTTOM, X, Y, BOTH
import tkinter as tk
from db.db.db_connect import get_connection
import os
from tkinter import PhotoImage
from fin_analytics import category_chart, monthly_chart
from tkinter import messagebox as msg
from datetime import datetime


class MainApp:
  def __init__(self, root):
    self.root = root
    self.root.title("FinTrack — Smart Expense Manager")
    self.root.geometry("1000x650")
    self.root.minsize(900, 600)
    self.style = Style(theme="flatly")
    self.current_theme = "flatly"
    self.current_currency = self.load_currency_preference().split()[0]


    try:
        with open("user_pref.txt", "r") as f:
           saved_theme = f.read().strip()
           if saved_theme in ("flatly", "darkly"):
              self.style.theme_use(saved_theme)
    except FileNotFoundError:
       pass          
           

    self._create_header()
    self._create_sidebar()
    self._create_main_area()

    self.frames = {}
    self._init_frames()
    self.show_frame("Home")

  # UI Building
  def _create_header(self):
    header = ttk.Frame(self.root, padding=(12, 8))
    header.pack(side=TOP, fill=X)

    title = ttk.Label(header, text="FinTrack", font=("Segoe UI", 18, "bold"))
    title.pack(side=LEFT, padx=(8, 12))

    tagline = ttk.Label(header, text="Smart Personal Expense & Budget Managment", font=("Segoe UI", 10))  
    tagline.pack(side=LEFT, padx=(4, 12))

    self.theme_btn = ttk.Button(
      header, text="🌙 Dark Mode", bootstyle="info-outline", command=self.toggle_theme
    )
    self.theme_btn.pack(side=RIGHT, padx=12)

  def _create_sidebar(self):
    sidebar = ttk.Frame(self.root, width=220, padding=(10, 10))
    sidebar.pack(side=LEFT, fill=Y)

    ttk.Label(sidebar, text="Navigation", font=("Segoe UI", 12, "bold")).pack(
      anchor="w", pady=(0, 8)
    )

    # Buttons
    btns = [
        ("Home", "primary", lambda: self.show_frame("Home")),
        ("Add Expense", "success", lambda: self.show_frame("Add")),
        ("Manage Expenses", "info-outline", lambda: self.show_frame("Manage")),
        ("Analytics", "primary", lambda: self.show_frame("Analytics")),
        ("Settings", "primary", lambda: self.show_frame("Settings")),
    ]

    for (text, style, cmd) in btns:
        b = ttk.Button(sidebar, text=text, width=20, command=cmd, bootstyle=style)
        b.pack(pady=6, anchor="w")

  def _create_main_area(self):
    self.main_area = ttk.Frame(self.root, padding=(12, 10))
    self.main_area.pack(side=LEFT, fill=BOTH, expand=True)

  def _init_frames(self):
    # -------------------- Home Frame --------------------
    self.frames["Home"] = HomeFrame(self.main_area, self)


    # -------------------- Add Expense Frame --------------------
    frm_add = ttk.Frame(self.main_area, padding=10)
    ttk.Label(frm_add, text="Add Expense", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

    form_frame = ttk.Frame(frm_add)
    form_frame.pack(anchor="w", pady=10)

    ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", pady=4)
    self.entry_date = ttk.Entry(form_frame, width=25)
    self.entry_date.grid(row=0, column=1, pady=4, padx=8)

    ttk.Label(form_frame, text="Category:").grid(row=1, column=0, sticky="w", pady=4)
    self.category_var = tk.StringVar()
    category_list = ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Health", "Other"]
    ttk.Combobox(form_frame, textvariable=self.category_var, values=category_list, width=22, state="readonly").grid(row=1, column=1, pady=4, padx=8)

    ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky="w", pady=4)
    self.entry_desc = ttk.Entry(form_frame, width=40)
    self.entry_desc.grid(row=2, column=1, pady=4, padx=8)

    ttk.Label(form_frame, text="Amount:").grid(row=3, column=0, sticky="w", pady=4)
    self.entry_amount = ttk.Entry(form_frame, width=25)
    self.entry_amount.grid(row=3, column=1, pady=4, padx=8)

    ttk.Button(frm_add, text="➕ Add Expense", bootstyle="success", command=self.add_expense).pack(anchor="w", pady=(10, 0))
    self.add_message = ttk.Label(frm_add, text="", font=("Segoe UI", 9))
    self.add_message.pack(anchor="w", pady=(6, 0))
    self.frames["Add"] = frm_add

    # -------------------- Manage Frame --------------------
    frm_manage = ttk.Frame(self.main_area)
    ttk.Label(frm_manage, text="📋 Manage Expenses", font=("Segoe UI", 16, "bold")).pack(pady=10)

    table_frame = ttk.Frame(frm_manage)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    y_scroll = ttk.Scrollbar(table_frame, orient="vertical")
    y_scroll.pack(side="right", fill="y")

    self.tree = ttk.Treeview(
        table_frame,
        columns=("id", "date", "category", "description", "amount"),
        show="headings",
        yscrollcommand=y_scroll.set,
        bootstyle="info"
    )
    self.tree.pack(fill="both", expand=True)
    y_scroll.config(command=self.tree.yview)

    self.tree.heading("id", text="ID")
    self.tree.heading("date", text="Date")
    self.tree.heading("category", text="Category")
    self.tree.heading("description", text="Description")
    self.tree.heading("amount", text=f"Amount ({getattr(self, 'current_currency', '₹')})")


    self.tree.column("id", width=50, anchor="center")
    self.tree.column("date", width=100)
    self.tree.column("category", width=120)
    self.tree.column("description", width=200)
    self.tree.column("amount", width=100, anchor="e")

    ttk.Button(frm_manage, text="🗑 Delete Selected", bootstyle="danger-outline", command=self.delete_selected).pack(pady=8)
    self.frames["Manage"] = frm_manage

    ttk.Button(frm_manage, text="🔄 Refresh", bootstyle="info-outline", command=self.load_expenses).pack(pady=5)

    ttk.Button(frm_manage, text="✏️ Edit Selected", bootstyle="info-outline", command=self.edit_selected).pack(pady=5)

    # -------------------- Analytics Frame --------------------
    frm_analytics = ttk.Frame(self.main_area)
    ttk.Label(frm_analytics, text="Analytics Dashboard", font=("Segoe UI", 14, "bold")).pack(anchor="nw", pady=(0, 10))

    chart_frame = ttk.Frame(frm_analytics)
    chart_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    cat_label = ttk.Label(chart_frame)
    cat_label.pack(side=LEFT, padx=10)

    month_label = ttk.Label(chart_frame)
    month_label.pack(side=RIGHT, padx=10)

    def refresh_charts():
        try:
            cat_path = category_chart()
            month_path = monthly_chart()

            if cat_path and os.path.exists(cat_path):
                cat_img = PhotoImage(file=cat_path)
                cat_label.config(image=cat_img)
                cat_label.image = cat_img

            if month_path and os.path.exists(month_path):
                month_img = PhotoImage(file=month_path)
                month_label.config(image=month_img)
                month_label.image = month_img
        except Exception as e:
            print("❌ Chart Error:", e)

    ttk.Button(frm_analytics, text="🔄 Refresh Charts", bootstyle="info-outline", command=refresh_charts).pack(pady=8)
    self.frames["Analytics"] = frm_analytics

      # Settings frame
    frm_settings = ttk.Frame(self.main_area)
    ttk.Label(frm_settings, text="Settings", font=("Segoe UI", 14, "bold")).pack(anchor="nw", pady=(0, 10))

    # Theme Selection
    theme_frame = ttk.LabelFrame(frm_settings, text="Theme", padding=10)
    theme_frame.pack(fill="x", pady=8)
    self.theme_var = tk.StringVar(value=self.current_theme)
    ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var, value="flatly").pack(anchor="w")
    ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var, value="darkly").pack(anchor="w")

    # Currency Selection
    currency_frame = ttk.LabelFrame(frm_settings, text="Currency", padding=10)
    currency_frame.pack(fill="x", pady=8)

    self.currency_var = tk.StringVar(value=self.load_currency_preference())
    currency_options = ["₹ (INR)", "$ (USD)", "€ (EUR)", "£ (GBP)"]
    self.currency_symbol_map = {
      "₹ (INR)": "₹",
      "$ (USD)": "$",
      "€ (EUR)": "€",
      "£ (GBP)": "£"
    }
    ttk.Combobox(currency_frame, textvariable=self.currency_var, values=currency_options, width=15, state="readonly").pack(anchor="w", pady=4)

    # Save Button
    ttk.Button(frm_settings, text="💾 Save Preferences", bootstyle="success", command=self.save_preferences).pack(pady=10)

    self.frames["Settings"] = frm_settings


    self.frames["Settings"] = SettingsFrame(self.main_area, self)

    # Place all frames (overlapping)
    for f in self.frames.values():
      f.place(relx=0, rely=0, relwidth=1, relheight=1)

  def load_expenses(self):
        """Fetch all expenses from DB and show in Treeview."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, date, category, description, amount FROM fin_expenses ORDER BY date DESC;"
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()

            # Clear old rows
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insert new rows
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            print("❌ Error loading expenses:", e)

  def delete_selected(self):
        """Delete selected record from database."""
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        record_id = item["values"][0]

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM fin_expenses WHERE id = %s", (record_id,))
            conn.commit()
            cur.close()
            conn.close()

            # Remove from Treeview
            self.tree.delete(selected[0])
            print(f"✅ Deleted record ID: {record_id}")
        except Exception as e:
            print("❌ Error deleting expense:", e)

  def edit_selected(self):
      """Open a popup to edit the selected expense."""
      selected_ids = self.tree.selection()
      if not selected_ids:
          msg.showwarning("Selection Error", "⚠️ Please select an expense to edit.")
          return
      
      first_item_id = selected_ids[0]
      item_details = self.tree.item(first_item_id)
      record = item_details["values"]
      try:
          record_id, date, category, description, amount = record
      except ValueError:
          msg.showerror("Data Error", "❌ Cannot retrieve complete data for the selected record.")
          return
  
      # Create popup
      edit_win = tk.Toplevel(self.root)
      edit_win.title(f"Edit Expense ID: {record_id}")
      edit_win.geometry("400x450")
      edit_win.resizable(False, False)

      # --- UI Fields ---
      ttk.Label(edit_win, text="Date (YYYY-MM-DD):").pack(anchor="w", padx=10, pady=(10, 0))
      entry_date = ttk.Entry(edit_win)
      entry_date.pack(fill="x", padx=10)
      entry_date.insert(0, date)

      ttk.Label(edit_win, text="Category:").pack(anchor="w", padx=10, pady=(10, 0))
      category_var = tk.StringVar(value=category)
      categories = ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Health", "Other"]
      ttk.Combobox(edit_win, textvariable=category_var, values=categories, state="readonly").pack(fill="x", padx=10)

      ttk.Label(edit_win, text="Description:").pack(anchor="w", padx=10, pady=(10, 0))
      entry_desc = ttk.Entry(edit_win)
      entry_desc.pack(fill="x", padx=10)
      entry_desc.insert(0, description)

      ttk.Label(edit_win, text="Amount:").pack(anchor="w", padx=10, pady=(10, 0))
      entry_amount = ttk.Entry(edit_win)
      entry_amount.pack(fill="x", padx=10)
      entry_amount.insert(0, amount)

        
      def save_changes():
        new_date = entry_date.get().strip()
        new_category = category_var.get().strip()
        new_desc = entry_desc.get().strip()
        new_amount_str = entry_amount.get().strip() # Get as string for validation

        if not new_date or not new_category or not new_amount_str:
            msg.showwarning("Warning", "All fields are required.")
            return

        try:
            datetime.strptime(new_date, "%Y-%m-%d")
            new_amount = float(new_amount_str) # Convert to float after validation
        except ValueError:
              msg.showerror("Invalid Format", "❌ Please check date (YYYY-MM-DD) or amount format.")
              return

            # Database Update
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE fin_expenses
                SET date = %s, category = %s, description = %s, amount = %s
                WHERE id = %s
                """,
                (new_date, new_category, new_desc, new_amount, record_id)
                )
            conn.commit()
            cur.close()
            conn.close()

            msg.showinfo("Success", f"✅ Expense ID {record_id} updated successfully!")
            edit_win.destroy()
            self.load_expenses() # Refresh the main table
        except Exception as e:
            msg.showerror("Database Error", f"❌ Failed to update expense: {e}")

      ttk.Button(edit_win, text="💾 Save Changes", bootstyle="success", command=save_changes).pack(pady=20, padx=10, fill='x')

  def show_frame(self, name):
    frame = self.frames.get(name)
    if frame:
      frame.lift()
      if name == "Manage":
        self.load_expenses()

      frame.lift()
    else:
      print(f"[FinTrack] frame '{name} not found")

  def toggle_theme(self):
    if self.current_theme in ("darkly", "solar", "superhero"):
      new_theme = "flatly"
      new_text = "🌙 Dark Mode"
    else:
      new_theme = "darkly"
      new_text = "☀️ Light Mode"

    try:
      self.style.theme_use(new_theme)
      self.current_theme = new_theme
      self.theme_btn.config(text=new_text)
      self.root.update_idletasks()
    except Exception as e:
      print("Theme switch failed:", e)

  def load_currency_preference(self):
    """Read saved currency from file."""
    try:
        with open("user_currency.txt", "r") as f:
            symbol = f.read().strip()
            if symbol:
                return symbol
    except FileNotFoundError:
        pass
    return "₹ (INR)"  # default

  def save_preferences(self):
    """Save selected theme and currency preference."""
    selected_theme = self.theme_var.get()
    selected_currency = self.currency_var.get()
    symbol = self.currency_symbol_map.get(selected_currency, "₹")

    # Save theme
    try:
        with open("user_pref.txt", "w") as f:
            f.write("dark" if selected_theme == "darkly" else "light")
    except Exception as e:
        print("❌ Error saving theme:", e)

    # Save currency
    try:
        with open("user_currency.txt", "w") as f:
            f.write(symbol)
    except Exception as e:
        print("❌ Error saving currency:", e)

    self.current_currency = symbol
    self.add_message.config(text=f"✅ Preferences saved ({symbol})!", foreground="green")

    # Apply theme immediately
    self.style.theme_use(selected_theme)


  def add_expense(self):
    from datetime import datetime
    date_str = self.entry_date.get().strip()
    category = self.category_var.get().strip()
    desc = self.entry_desc.get().strip()
    amount_str = self.entry_amount.get().strip()

    if not date_str or not category or not amount_str:
      self.add_message.config(text="⚠️ Please fill in all required fields.", foreground="orange")
      return

    try:
      datetime.strptime(date_str, "%Y-%m-%d")
      amount = float(amount_str)
    except ValueError:
      self.add_message.config(text="❌ Invalid date or amount format.", foreground="red")
      return

    # Insert into PostgreSQL
    try:
      conn = get_connection()
      cur = conn.cursor()
      cur.execute(
        "INSERT INTO fin_expenses (date, category, description, amount) VALUES (%s, %s, %s, %s)",
        (date_str, category, desc, amount),
      )
      conn.commit()
      cur.close()
      conn.close()
      self.add_message.config( text=f"✅ Expense added successfully! ({getattr(self, 'current_currency', '₹')})",
      foreground="green")

      # Clear fields
      self.entry_date.delete(0, tk.END)
      self.entry_desc.delete(0, tk.END)
      self.entry_amount.delete(0, tk.END)
      self.category_var.set("")
    except Exception as e:
      self.add_message.config(text=f"❌ Database Error: {e}", foreground="red")


def main():
  root = tb.Window(themename="flatly")
  app = MainApp(root)
  root.mainloop()


class HomeFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(
            self, text="🏠 FinTrack Dashboard", font=("Segoe UI", 16, "bold")
        ).pack(pady=10, anchor="w")

        self.summary_label = ttk.Label(
            self, text="Fetching data...", font=("Segoe UI", 11), justify=LEFT
        )
        self.summary_label.pack(pady=10, anchor="w")

        ttk.Label(
            self, text="🕓 Recent Expenses", font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(20, 5))

        # ---- Scrollable table ----
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="x", pady=5)

        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        y_scroll.pack(side=RIGHT, fill="y")

        self.recent_tree = ttk.Treeview(
            tree_frame,
            columns=("date", "category", "description", "amount"),
            show="headings",
            yscrollcommand=y_scroll.set,
            bootstyle="info"
        )
        self.recent_tree.pack(fill="x", expand=True)
        y_scroll.config(command=self.recent_tree.yview)

        self.recent_tree.heading("date", text="Date")
        self.recent_tree.heading("category", text="Category")
        self.recent_tree.heading("description", text="Description")
        self.recent_tree.heading(
            "amount", text=f"Amount ({getattr(self.app, 'current_currency', '₹')})"
        )

        # ---- Buttons ----
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=15)

        ttk.Button(
            btn_frame,
            text="➕ Add Expense",
            bootstyle="success",
            command=lambda: self.app.show_frame("Add"),
        ).pack(side=LEFT, padx=10)

        ttk.Button(
            btn_frame,
            text="📊 View Analytics",
            bootstyle="info",
            command=lambda: self.app.show_frame("Analytics"),
        ).pack(side=LEFT, padx=10)

        ttk.Button(
            btn_frame,
            text="🔄 Refresh",
            bootstyle="secondary-outline",
            command=self.refresh_dashboard,  # <-- references method below
        ).pack(side=LEFT, padx=10)

        # --- initialize content ---
        self.refresh_dashboard()  # <-- safely called after method exists


    def refresh_dashboard(self):
        """Fetch total, top category, and recent transactions"""
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM fin_expenses
                WHERE DATE_TRUNC('month', date) = DATE_TRUNC('month', CURRENT_DATE);
            """)
            total = cur.fetchone()[0] or 0

            cur.execute("""
                SELECT category, SUM(amount)
                FROM fin_expenses
                GROUP BY category
                ORDER BY SUM(amount) DESC
                LIMIT 1;
            """)
            top_cat = cur.fetchone()
            top_category = f"{top_cat[0]} (₹{top_cat[1]:.2f})" if top_cat else "N/A"

            summary_text = (
                f"💰 Total Spent This Month: ₹{total:.2f}\n"
                f"🏷️ Top Category: {top_category}"
            )
            self.summary_label.config(text=summary_text)

            cur.execute("""
                SELECT date, category, description, amount
                FROM fin_expenses
                ORDER BY date DESC
                LIMIT 5;
            """)
            rows = cur.fetchall()

            for i in self.recent_tree.get_children():
                self.recent_tree.delete(i)
            for r in rows:
                self.recent_tree.insert("", "end", values=r)

            cur.close()
            conn.close()

        except Exception as e:
            self.summary_label.config(text=f"❌ Error loading data: {e}")


class SettingsFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="⚙️ Settings", font=("Segoe UI", 14, "bold")).pack(pady=15)

        # --- Theme Switch ---
        ttk.Label(self, text="Choose Theme:").pack(pady=(10, 0))

        self.theme_var = tk.StringVar(value=self.load_preference())
        dark_btn = ttk.Radiobutton(
            self, text="Dark Mode", variable=self.theme_var, value="dark"
        )
        dark_btn.pack(anchor="w", padx=20)
        light_btn = ttk.Radiobutton(
            self, text="Light Mode", variable=self.theme_var, value="light"
        )
        light_btn.pack(anchor="w", padx=20)

        ttk.Button(
            self, text="💾 Apply Theme", bootstyle="success", command=self.apply_theme
        ).pack(pady=15)

        ttk.Separator(self, orient="horizontal").pack(fill=X, pady=10)

        # --- Other Settings Example ---
        ttk.Label(self, text="Currency Symbol:").pack(pady=(10, 0))
        self.currency_var = tk.StringVar(value=self.load_currency())
        currency_menu = ttk.Combobox(
            self,
            textvariable=self.currency_var,
            values=["₹", "$", "€", "£"],
            state="readonly",
        )
        currency_menu.pack(pady=(0, 10))

        ttk.Button(
            self, text="💾 Save All Settings", bootstyle="primary", command=self.save_all
        ).pack(pady=10)

    def load_preference(self):
        try:
            with open("user_pref.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "dark"

    def load_currency(self):
        try:
            with open("currency_pref.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "₹"

    def apply_theme(self):
        theme = self.theme_var.get()
        try:
            self.app.style.theme_use(theme)
            msg.showinfo("Theme Applied", f"🎨 Switched to {theme.capitalize()} Mode")
        except Exception as e:
            msg.showerror("Error", f"Theme not applied: {e}")

    def save_all(self):
        with open("user_pref.txt", "w") as f:
            f.write(self.theme_var.get())
        with open("currency_pref.txt", "w") as f:
            f.write(self.currency_var.get())
        msg.showinfo("✅ Saved", "Settings saved successfully!")


if __name__ == "__main__":
  main()