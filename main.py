import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import hashlib
import os

# -------------------- File Setup --------------------
USER_FILE = "users.txt"
if not os.path.exists(USER_FILE):
    open(USER_FILE, "w").close()

# -------------------- Utility Functions --------------------
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

# -------------------- Login Action --------------------
def login_action():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Warning", "Please fill in all fields.")
        return

    if validate_user(username, password):
        open_welcome_window(username)
    else:
        messagebox.showerror("Error", "Invalid credentials")

# -------------------- Signup Window --------------------
def open_signup_window():
    signup_window = tk.Toplevel()
    signup_window.title("Sign Up")
    signup_window.geometry("320x220")

    # ----- Create a container frame -----
    container = tk.Frame(signup_window)
    container.place(relx=0.5, rely=0.5, anchor="center")  # Center the form

    # ----- Form widgets inside the container -----
    ttk.Label(container, text="Create Account", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)

    ttk.Label(container, text="Username:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    signup_username = ttk.Entry(container)
    signup_username.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(container, text="Password:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    signup_password = ttk.Entry(container, show="*")
    signup_password.grid(row=2, column=1, padx=5, pady=5)

    def signup_action():
        username = signup_username.get().strip()
        password = signup_password.get().strip()

        if not username or not password:
            messagebox.showwarning("Warning", "Please fill in all fields.")
            return

        if user_exists(username):
            messagebox.showerror("Error", "Username already exists")
        else:
            save_user(username, password)
            messagebox.showinfo("Success", "Signup successful!")
            signup_window.destroy()

    ttk.Button(container, text="Signup", command=signup_action).grid(row=3, column=0, columnspan=2, pady=15)


# -------------------- Welcome Window --------------------
def open_welcome_window(username):
    welcome_window = tk.Toplevel()
    welcome_window.title("Welcome")
    welcome_window.geometry("250x100")
    ttk.Label(welcome_window, text=f"Welcome, {username}!", font=("Arial", 12)).pack(pady=30)

# -------------------- Main UI --------------------
root = tk.Tk()
root.title("Login Page")
root.geometry("800x400")

# Left: Image
left_frame = tk.Frame(root, width=400, height=400)
left_frame.pack(side="left", fill="both")

bg_image = Image.open("background.jpg")  # <- Change this if needed
bg_image = bg_image.resize((400, 400), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

image_label = tk.Label(left_frame, image=bg_photo)
image_label.place(x=0, y=0, relwidth=1, relheight=1)

# Right: Form
right_frame = tk.Frame(root, width=400, height=400, bg="white")
right_frame.place(x=400, y=0, width=400, height=400)

title_label = tk.Label(right_frame, text="Login", font=("Arial", 20, "bold"), bg="white", fg="#333")
title_label.pack(pady=30)

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

