import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import card_details        # module to manage cards
import transactions        # module to handle transactions
import Login               # your login/register module


def open_banking_app():
    """Open the expense tracker app directly."""
    from banking_app import ExpenseTracker   # import the class
    tracker_root = tk.Toplevel()             # new Tkinter window
    app = ExpenseTracker(tracker_root)       # start the ExpenseTracker
    tracker_root.mainloop()


def option_two(username):
    """Open the add card window for this user."""
    card_details.add_card_window(username)


def option_three(username):
    """Open the transaction window for this user."""
    transactions.transaction_window(username)


def logout(root):
    """Log out the current user and go back to login/register page."""
    if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
        root.destroy()
        Login.show_login_window()  # Call your login/register window function


def run_main_menu(username=None):
    root = tk.Tk()
    root.title("Main Menu")
    root.geometry("400x400")
    root.config(bg="#f0f8ff")

    if username:
        tk.Label(root, text=f"Welcome, {username}!", font=("Arial", 12, "bold"), bg="#f0f8ff").pack(pady=5)

    tk.Label(root, text="Select an Option", font=("Arial", 14, "bold"), bg="#f0f8ff").pack(pady=20)

    tk.Button(root, text="Expense Tracker", command=open_banking_app, bg="#90ee90", width=25).pack(pady=10)
    tk.Button(root, text="Manage Cards", command=lambda: option_two(username), bg="#add8e6", width=25).pack(pady=10)
    tk.Button(root, text="Transactions", command=lambda: option_three(username), bg="#ffcccb", width=25).pack(pady=10)
    tk.Button(root, text="Logout", command=lambda: logout(root), bg="#ffa500", width=25).pack(pady=10)
    tk.Button(root, text="Exit", command=root.quit, bg="#f08080", width=25).pack(pady=20)

    root.mainloop()
