import tkinter as tk
from tkinter import messagebox
import os

# File to store user credentials
USER_FILE = "users.txt"

# Create the users file if it doesn't exist
if not os.path.exists(USER_FILE):
    open(USER_FILE, "w").close()


def save_user(username, password):
    with open(USER_FILE, "a") as f:
        f.write(f"{username},{password}\n")


def user_exists(username):
    with open(USER_FILE, "r") as f:
        for line in f:
            stored_user, _ = line.strip().split(",")
            if stored_user == username:
                return True
    return False


def validate_user(username, password):
    with open(USER_FILE, "r") as f:
        for line in f:
            stored_user, stored_pass = line.strip().split(",")
            if stored_user == username and stored_pass == password:
                return True
    return False


# ---------- Signup Window ----------
def open_signup_window():
    signup_window = tk.Toplevel()
    signup_window.title("Signup")
    signup_window.geometry("300x250")

    tk.Label(signup_window, text="Create an Account", font=("Arial", 14)).pack(pady=10)

    tk.Label(signup_window, text="Username").pack()
    username_entry = tk.Entry(signup_window)
    username_entry.pack()

    tk.Label(signup_window, text="Password").pack()
    password_entry = tk.Entry(signup_window, show="*")
    password_entry.pack()

    def signup_action():
        username = username_entry.get()
        password = password_entry.get()

        if user_exists(username):
            messagebox.showerror("Error", "Username already exists")
        else:
            save_user(username, password)
            messagebox.showinfo("Success", "Signup successful")
            signup_window.destroy()

    tk.Button(signup_window, text="Signup", command=signup_action).pack(pady=10)


# ---------- Login Window ----------
def login_action():
    username = username_entry.get()
    password = password_entry.get()

    if validate_user(username, password):
        messagebox.showinfo("Success", f"Welcome, {username}!")
    else:
        messagebox.showerror("Error", "Invalid credentials")


root = tk.Tk()
root.title("Login Page")
root.geometry("300x250")

tk.Label(root, text="Login", font=("Arial", 14)).pack(pady=10)

tk.Label(root, text="Username").pack()
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="Password").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Button(root, text="Login", command=login_action).pack(pady=10)
tk.Button(root, text="Create Account", command=open_signup_window).pack()

root.mainloop()
