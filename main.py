import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import hashlib
import os
import sqlite3
import datetime
from tkcalendar import DateEntry
import csv

# ---------- SQLite Setup ----------
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        type TEXT,
        amount REAL,
        description TEXT,
        category TEXT,
        date TEXT
    )
""")
conn.commit()

# ---------- User Storage ----------
USER_FILE = "users.txt"
if not os.path.exists(USER_FILE):
    open(USER_FILE, "w").close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user(username, password):
    with open(USER_FILE, "a") as f:
        f.write(f"{username},{hash_password(password)}\n")

def user_exists(username):
    with open(USER_FILE, "r") as f:
        for line in f:
            stored_user, _ = line.strip().split(",")
            if stored_user == username:
                return True
    return False

def validate_user(username, password):
    hashed = hash_password(password)
    with open(USER_FILE, "r") as f:
        for line in f:
            stored_user, stored_pass = line.strip().split(",")
            if stored_user == username and stored_pass == hashed:
                return True
    return False

# ---------- Transactions ----------
def save_transaction(username, txn_type, amount, description, date, category=None):
    # date = datetime.date.today().isoformat()
    # print(date) ##2025-07-04
    cursor.execute(
        "INSERT INTO transactions (username, type, amount, description, category, date) VALUES (?, ?, ?, ?, ?, ?)",
        (username, txn_type, amount, description, category, date)
    )
    conn.commit()

def load_transactions(username, txn_type):
    cursor.execute(
        "SELECT amount, description, category, date FROM transactions WHERE username=? AND type=? ORDER BY date ASC",
        (username, txn_type)
    )
    return cursor.fetchall()

# ---------- Signup ----------
def signup_action(signup_window, username_entry, password_entry):
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Warning", "Please fill in all fields.")
        return

    if user_exists(username):
        messagebox.showerror("Error", "Username already exists")
    else:
        save_user(username, password)
        messagebox.showinfo("Success", "Signup successful!")
        signup_window.destroy()

def open_signup_window():
    signup_window = tk.Toplevel()
    signup_window.title("Sign Up")
    signup_window.geometry("320x220")
    signup_window.resizable(False, False)

    container = tk.Frame(signup_window)
    container.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Label(container, text="Create Account", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)

    ttk.Label(container, text="Username:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    username_entry = ttk.Entry(container)
    username_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(container, text="Password:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    password_entry = ttk.Entry(container, show="*")
    password_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Button(container, text="Signup",
               command=lambda: signup_action(signup_window, username_entry, password_entry)
               ).grid(row=3, column=0, columnspan=2, pady=15)

# ---------- Dashboard ----------
def update_balance(username, balance_var):
    income_total = sum(float(row[0]) for row in load_transactions(username, "income"))
    expense_total = sum(float(row[0]) for row in load_transactions(username, "expense"))
    balance = income_total - expense_total
    balance_var.set(f"₹{balance:.2f}")

def open_add_income(username, balance_var):
    win = tk.Tk()
    win.title("Add Income")
    win.geometry("300x200")

    ttk.Label(win, text="Amount:").pack(pady=5)
    amount_entry = ttk.Entry(win)
    amount_entry.pack()

    ttk.Label(win, text="Description:").pack(pady=5)
    desc_entry = ttk.Entry(win)
    desc_entry.pack()

    ttk.Label(win, text = "Date:").pack(pady=5)
    date_entry = DateEntry(win, width=15, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    date_entry.pack()

    def save():
        try:
            amount = float(amount_entry.get())
            desc = desc_entry.get()
            save_transaction(username, "income", amount, desc, date_entry.get())
            win.destroy()
            update_balance(username, balance_var)
            messagebox.showinfo("Saved", "Income added!")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")

    ttk.Button(win, text="Save", command=save).pack(pady=10)

def open_add_expense(username, balance_var):
    win = tk.Tk()
    win.title("Add Expense")
    win.geometry("300x250")

    ttk.Label(win, text="Amount:").pack(pady=5)
    amount_entry = ttk.Entry(win)
    amount_entry.pack()

    ttk.Label(win, text="Description:").pack(pady=5)
    desc_entry = ttk.Entry(win)
    desc_entry.pack()

    ttk.Label(win, text = "Date:").pack(pady=5)
    date_entry = DateEntry(win, width=15, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    date_entry.pack()

    def save():
        try:
            amount = float(amount_entry.get())
            desc = desc_entry.get()
            save_transaction(username, "expense", amount, desc, date_entry.get())
            win.destroy()
            update_balance(username, balance_var)
            messagebox.showinfo("Saved", "Expense added!")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")

    ttk.Button(win, text="Save", command=save).pack(pady=10)

def view_transactions(username):
    win = tk.Toplevel()
    win.title("Transactions")
    win.geometry("600x480")
    # win.resizable(False, False)
    win.configure(bg="#f9f9f9")

    #Incomes
    ttk.Label(win, text="Income", font=("Arial", 16, "bold"), background="#f9f9f9").pack(pady=10)

    tree_frame1 = ttk.Frame(win)
    tree_frame1.pack(fill="both", expand=True, padx=10, pady=10)

    tree_scroll1 = ttk.Scrollbar(tree_frame1)
    tree_scroll1.pack(side="right", fill="y")

    tree1 = ttk.Treeview(tree_frame1, yscrollcommand=tree_scroll1.set, columns=("type", "date", "amount", "desc"), show="headings", height=7)
    tree1.pack(fill="both", expand=True)
    tree_scroll1.config(command=tree1.yview)

    tree1.heading("type", text="Type")
    tree1.heading("date", text="Date")
    tree1.heading("amount", text="Amount (₹)")
    tree1.heading("desc", text="Description")

    tree1.column("type", width=80, anchor="center")
    tree1.column("date", width=100, anchor="center")
    tree1.column("amount", width=100, anchor="center")
    tree1.column("desc", width=200, anchor="w")

    for amount, desc, _, date in load_transactions(username, "income"):
        tree1.insert("", "end", values=("Income", date, f"₹{amount:.2f}", desc))


    #Expenses
    ttk.Label(win, text="Expense", font=("Arial", 16, "bold"), background="#f9f9f9").pack(pady=10)

    tree_frame2 = ttk.Frame(win)
    tree_frame2.pack(fill="both", expand=True, padx=10, pady=(10, 20))

    tree_scroll2 = ttk.Scrollbar(tree_frame2)
    tree_scroll2.pack(side="right", fill="y")

    tree2 = ttk.Treeview(tree_frame2, yscrollcommand=tree_scroll2.set, columns=("type", "date", "amount", "desc"), show="headings", height = 7)
    tree2.pack(fill="both", expand=True)
    tree_scroll2.config(command=tree2.yview)

    tree2.heading("type", text="Type")
    tree2.heading("date", text="Date")
    tree2.heading("amount", text="Amount (₹)")
    tree2.heading("desc", text="Description")

    tree2.column("type", width=80, anchor="center")
    tree2.column("date", width=100, anchor="center")
    tree2.column("amount", width=100, anchor="center")
    tree2.column("desc", width=200, anchor="w")

    for amount, desc, _, date in load_transactions(username, "expense"):
        tree2.insert("", "end", values=("Expense", date, f"₹{amount:.2f}", desc))


def getFullSummary():
    # Fetch income data
    cursor.execute("SELECT date, amount FROM transactions WHERE type='income' ORDER BY date ASC")
    income_data = cursor.fetchall()

    # Fetch expense data
    cursor.execute("SELECT date, amount FROM transactions WHERE type='expense' ORDER BY date ASC")
    expense_data = cursor.fetchall()

    if not income_data and not expense_data:
        messagebox.showinfo("Info", "No data to display.")
        return

    # Prepare data for plotting
    income_dates = [row[0] for row in income_data]
    income_amounts = [row[1] for row in income_data]

    expense_dates = [row[0] for row in expense_data]
    expense_amounts = [row[1] for row in expense_data]

    # Create figure
    plt.figure(figsize=(10, 6))

    # Plot income
    if income_data:
        plt.bar(income_dates, income_amounts, label="Income", color="green")
    # Plot expense
    if expense_data:
        plt.bar(expense_dates,expense_amounts, label="Expense", color="red")

    plt.title("Income & Expense Over Time")
    plt.xlabel("Date")
    plt.ylabel("Amount (₹)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


def DrawSummary():
    summaryWindow = tk.Toplevel()
    summaryWindow.title("Summary")
    summaryWindow.geometry("400x350")
    summaryWindow.configure(bg="#f9f9f9")
    summaryWindow.resizable(False, False)

    container = tk.Frame(summaryWindow, bg="#f9f9f9")
    container.pack(expand=True, fill="both", padx=20, pady=20)

    ttk.Label(container, text="Summary Report", font=("Arial", 16, "bold"), background="#f9f9f9").pack(pady=(0, 15))
    ttk.Button(container, text="📊 View Full Summary", command=getFullSummary).pack(pady=5)

    # Date Filter Label
    ttk.Label(container, text="Filter by Date", font=("Arial", 12, "bold"), background="#f9f9f9").pack(pady=(20, 5))

    # Date Picker Fields
    form_frame = tk.Frame(container, bg="#f9f9f9")
    form_frame.pack()

    ttk.Label(form_frame, text="From:", background="#f9f9f9").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    from_entry = DateEntry(form_frame, width=15, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    from_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="To:", background="#f9f9f9").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    to_entry = DateEntry(form_frame, width=15, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    to_entry.grid(row=1, column=1, padx=5, pady=5)

    def get_filtered():
        from_date = from_entry.get()
        to_date = to_entry.get()
        if not from_date or not to_date:
            messagebox.showerror("Error", "Please enter both dates.")
            return

        cursor.execute("SELECT date, amount FROM transactions WHERE type='income' and date BETWEEN ? AND ?", (from_date, to_date))
        income_data = cursor.fetchall()

        cursor.execute("SELECT date, amount FROM transactions WHERE type='expense' and date BETWEEN ? AND ?", (from_date, to_date))
        expense_data = cursor.fetchall()

        if not income_data and not expense_data:
            messagebox.showinfo("Info", "No data to display.")
            return

        income_dates = [row[0] for row in income_data]
        income_amounts = [row[1] for row in income_data]
        expense_dates = [row[0] for row in expense_data]
        expense_amounts = [row[1] for row in expense_data]

        plt.figure(figsize=(10, 6))
        if income_data:
            plt.bar(income_dates, income_amounts, label="Income", color="green")
        if expense_data:
            plt.bar(expense_dates, expense_amounts, label="Expense", color="red")
        plt.title("Income & Expense (Filtered)")
        plt.xlabel("Date")
        plt.ylabel("Amount (₹)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()

    ttk.Button(container, text="🔍 Filter Summary", command=get_filtered).pack(pady=15)
    
def exportToCSV():
    cursor.execute("Select * from transactions")
    data=cursor.fetchall()
    file=open("Data.csv",'w',newline="", encoding="utf-8")
    writer=csv.writer(file)
    writer.writerow(["Id", "Username", "Type", "Amount", "Description","Category","Date"])
    writer.writerows(data)

def open_dashboard_window(username):
    win = tk.Tk()  
    win.title("Dashboard")
    win.geometry("600x450")
    win.configure(bg="#f2f2f2")
    win.resizable(False, False)

    # ---------- Welcome Message ----------
    tk.Label(win, text=f"Welcome, {username}!", font=("Arial", 18, "bold"), bg="#f2f2f2").pack(pady=20)

    # ---------- Current Balance ----------
    balance_var = tk.StringVar()
    balance_frame = tk.Frame(win, bg="#f2f2f2")
    balance_frame.pack()
    tk.Label(balance_frame, text="Current Balance:", font=("Arial", 14), bg="#f2f2f2").grid(row=0, column=0, sticky="e")
    tk.Label(balance_frame, textvariable=balance_var, font=("Arial", 14, "bold"), fg="green", bg="#f2f2f2").grid(row=0, column=1, padx=10, sticky="w")
    update_balance(username, balance_var)

    # ---------- Button Group ----------
    btn_frame = tk.Frame(win, bg="#f2f2f2")
    btn_frame.pack(pady=30)

    ttk.Button(btn_frame, text="➕ Add Income", width=20, command=lambda: open_add_income(username, balance_var)).grid(row=0, column=0, padx=10, pady=5)
    ttk.Button(btn_frame, text="➖ Add Expense", width=20, command=lambda: open_add_expense(username, balance_var)).grid(row=0, column=1, padx=10, pady=5)
    ttk.Button(btn_frame, text="📄 View Transactions", width=42, command=lambda: view_transactions(username)).grid(row=1, column=0, columnspan=2, pady=10)

    # ---------- Extra Controls ----------
    bottom_btn_frame = tk.Frame(win, bg="#f2f2f2")
    bottom_btn_frame.pack(pady=10)

    ttk.Button(bottom_btn_frame, text="📈 Summary", width=20, command=DrawSummary).grid(row=0, column=0, padx=20)
    ttk.Button(bottom_btn_frame, text="📁 Export to CSV", width=20, command=exportToCSV).grid(row=0, column=1, padx=20)

    # ---------- Logout ----------
    ttk.Button(win, text="🚪 Logout", command=win.destroy).pack(side="bottom", pady=15)


# ---------- Login ----------
def login_action():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Warning", "Please fill in all fields.")
        return

    if validate_user(username, password):
        root.destroy()
        open_dashboard_window(username)
    else:
        messagebox.showerror("Error", "Invalid credentials")

# ---------- UI ----------
root = tk.Tk()
root.title("Login Page")
root.geometry("800x400")
root.resizable(False, False)

left_frame = tk.Frame(root, width=400, height=400)
left_frame.pack(side="left", fill="both")

bg_image = Image.open("background.jpg")
bg_image = bg_image.resize((400, 400), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

tk.Label(left_frame, image=bg_photo).place(x=0, y=0, relwidth=1, relheight=1)

right_frame = tk.Frame(root, width=400, height=400, bg="white")
right_frame.place(x=400, y=0, width=400, height=400)

tk.Label(right_frame, text="Login", font=("Arial", 20, "bold"), bg="white", fg="#333").pack(pady=30)

form_frame = tk.Frame(right_frame, bg="white")
form_frame.pack(pady=10)

ttk.Label(form_frame, text="Username:", background="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
username_entry = ttk.Entry(form_frame)
username_entry.grid(row=0, column=1, padx=10, pady=10)

ttk.Label(form_frame, text="Password:", background="white").grid(row=1, column=0, padx=10, pady=10, sticky="e")
password_entry = ttk.Entry(form_frame, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=10)

ttk.Button(right_frame, text="Login", command=login_action).pack(pady=10)
ttk.Button(right_frame, text="Create Account", command=open_signup_window).pack()

root.mainloop()
