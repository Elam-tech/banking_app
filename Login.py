import tkinter as tk
from tkinter import messagebox
import Main_Menu
import os

USERS_FILE = "users.txt"

def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            for line in file:
                username, password = line.strip().split(",")
                users[username] = password
    return users

def save_user(username, password):
    with open(USERS_FILE, "a") as file:
        file.write(f"{username},{password}\n")

def switch_to_register():
    login_frame.pack_forget()
    register_frame.pack(pady=20)

def switch_to_login():
    register_frame.pack_forget()
    login_frame.pack(pady=20)

def register_user():
    username = reg_username_entry.get().strip()
    password = reg_password_entry.get().strip()

    if not username or not password:
        messagebox.showerror("Error", "Both fields are required!")
        return

    users = load_users()
    if username in users:
        messagebox.showerror("Error", "Username already exists!")
        return

    save_user(username, password)
    messagebox.showinfo("Success", "Account created successfully!")
    switch_to_login()

def verify_login():
    username = login_username_entry.get().strip()
    password = login_password_entry.get().strip()

    users = load_users()
    if username in users and users[username] == password:
        root.destroy()
        # Pass the username to the main menu
        Main_Menu.run_main_menu(username)
    else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
    
def show_login_window():
        global root
        root = tk.Tk()
        root.title("Login / Register")
        root.geometry("350x250")
        root.config(bg="#f0f8ff")
    
        # ===== LOGIN FRAME =====
        global login_frame, login_username_entry, login_password_entry
        login_frame = tk.Frame(root, bg="#f0f8ff")
        tk.Label(login_frame, text="Login", font=("Arial", 14, "bold"), bg="#f0f8ff").pack(pady=10)
    
        tk.Label(login_frame, text="Username:", bg="#f0f8ff").pack()
        login_username_entry = tk.Entry(login_frame)
        login_username_entry.pack(pady=5)
    
        tk.Label(login_frame, text="Password:", bg="#f0f8ff").pack()
        login_password_entry = tk.Entry(login_frame, show="*")
        login_password_entry.pack(pady=5)
    
        tk.Button(login_frame, text="Login", command=verify_login, bg="#90ee90", width=15).pack(pady=10)
        tk.Button(login_frame, text="Create Account", command=switch_to_register, bg="#add8e6", width=15).pack()
    
        login_frame.pack(pady=20)
    
        # ===== REGISTER FRAME =====
        global register_frame, reg_username_entry, reg_password_entry
        register_frame = tk.Frame(root, bg="#f0f8ff")
        tk.Label(register_frame, text="Create Account", font=("Arial", 14, "bold"), bg="#f0f8ff").pack(pady=10)
    
        tk.Label(register_frame, text="Username:", bg="#f0f8ff").pack()
        reg_username_entry = tk.Entry(register_frame)
        reg_username_entry.pack(pady=5)
    
        tk.Label(register_frame, text="Password:", bg="#f0f8ff").pack()
        reg_password_entry = tk.Entry(register_frame, show="*")
        reg_password_entry.pack(pady=5)
    
        tk.Button(register_frame, text="Register", command=register_user, bg="#90ee90", width=15).pack(pady=10)
        tk.Button(register_frame, text="Back to Login", command=switch_to_login, bg="#ffcccb", width=15).pack()
    
        root.mainloop()

if __name__ == "__main__":
    show_login_window()
