import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import hashlib
import os
import sqlite3
import datetime

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
def save_transaction(username, txn_type, amount, description, category=None):
    date = datetime.date.today().isoformat()
    cursor.execute(
        "INSERT INTO transactions (username, type, amount, description, category, date) VALUES (?, ?, ?, ?, ?, ?)",
        (username, txn_type, amount, description, category, date)
    )
    conn.commit()

def load_transactions(username, txn_type):
    cursor.execute(
        "SELECT amount, description, category, date FROM transactions WHERE username=? AND type=?",
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

    def save():
        try:
            amount = float(amount_entry.get())
            desc = desc_entry.get()
            save_transaction(username, "income", amount, desc)
            messagebox.showinfo("Saved", "Income added!")
            win.destroy()
            update_balance(username, balance_var)
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

    ttk.Label(win, text="Category:").pack(pady=5)
    category_entry = ttk.Entry(win)
    category_entry.pack()

    def save():
        try:
            amount = float(amount_entry.get())
            desc = desc_entry.get()
            category = category_entry.get()
            save_transaction(username, "expense", amount, desc, category)
            messagebox.showinfo("Saved", "Expense added!")
            win.destroy()
            update_balance(username, balance_var)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")

    ttk.Button(win, text="Save", command=save).pack(pady=10)

def view_transactions(username):
    win = tk.Tk()
    win.title("Transactions")
    win.geometry("400x300")

    ttk.Label(win, text="Incomes", font=("Arial", 12, "bold")).pack()
    for amount, desc, _, date in load_transactions(username, "income"):
        ttk.Label(win, text=f"{date} - ₹{amount} ({desc})").pack()

    ttk.Label(win, text="Expenses", font=("Arial", 12, "bold")).pack(pady=(10, 0))
    for amount, desc, cat, date in load_transactions(username, "expense"):
        ttk.Label(win, text=f"{date} - ₹{amount} ({desc} - {cat})").pack()

def open_dashboard_window(username):
    win = tk.Tk()
    win.title("Dashboard")
    win.geometry("600x400")
    win.configure(bg="#f2f2f2")

    tk.Label(win, text=f"Welcome, {username}!", font=("Arial", 18, "bold"), bg="#f2f2f2").pack(pady=20)

    balance_var = tk.StringVar()
    tk.Label(win, text="Current Balance:", font=("Arial", 14), bg="#f2f2f2").pack()
    tk.Label(win, textvariable=balance_var, font=("Arial", 16, "bold"), fg="green", bg="#f2f2f2").pack(pady=5)

    update_balance(username, balance_var)

    btn_frame = tk.Frame(win, bg="#f2f2f2")
    btn_frame.pack(pady=20)

    ttk.Button(btn_frame, text="➕ Add Income", command=lambda: open_add_income(username, balance_var)).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="➖ Add Expense", command=lambda: open_add_expense(username, balance_var)).grid(row=0, column=1, padx=10)
    ttk.Button(btn_frame, text="📄 View Transactions", command=lambda: view_transactions(username)).grid(row=1, column=0, columnspan=2, pady=10)

    ttk.Button(win, text="🚪 Logout", command=win.destroy).pack(side="bottom", pady=20)

# ---------- Login ----------
def login_action():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Warning", "Please fill in all fields.")
        return

    if validate_user(username, password):
        open_dashboard_window(username)
        root.destroy()
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
