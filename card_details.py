import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from cryptography.fernet import Fernet

# Encryption key (should ideally be stored securely)
KEY_FILE = "secret.key"
CARD_FILE = "card_details.txt"

# Generate a key if not exists
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
else:
    with open(KEY_FILE, "rb") as f:
        key = f.read()

fernet = Fernet(key)

def encrypt_data(data):
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data):
    return fernet.decrypt(data.encode()).decode()

def load_cards(username):
    """Load all cards for a specific user."""
    cards = []
    if os.path.exists(CARD_FILE):
        with open(CARD_FILE, "r") as file:
            for line in file:
                try:
                    user_enc, card_enc, expiry_enc, cvv_enc, balance_enc = line.strip().split(",")
                    user = decrypt_data(user_enc)
                    if user == username:
                        cards.append({
                            "card_number": decrypt_data(card_enc),
                            "expiry": decrypt_data(expiry_enc),
                            "cvv": decrypt_data(cvv_enc),
                            "balance": float(decrypt_data(balance_enc))
                        })
                except:
                    continue  # Skip corrupted lines
    return cards

def save_card(username, card_number, expiry, cvv, balance=0):
    with open(CARD_FILE, "a") as file:
        line = ",".join([
            encrypt_data(username),
            encrypt_data(card_number),
            encrypt_data(expiry),
            encrypt_data(cvv),
            encrypt_data(str(balance))
        ])
        file.write(line + "\n")

def update_card_balance(username, card_number, new_balance):
    lines = []
    if os.path.exists(CARD_FILE):
        with open(CARD_FILE, "r") as file:
            lines = file.readlines()

    with open(CARD_FILE, "w") as file:
        for line in lines:
            try:
                user_enc, card_enc, expiry_enc, cvv_enc, balance_enc = line.strip().split(",")
                user = decrypt_data(user_enc)
                card = decrypt_data(card_enc)
                if user == username and card == card_number:
                    balance_enc = encrypt_data(str(new_balance))
                file.write(",".join([user_enc, card_enc, expiry_enc, cvv_enc, balance_enc]) + "\n")
            except:
                file.write(line)  # preserve corrupted lines

def add_card_window(username):
    """Window to add new card or add funds."""
    def save_new_card():
        card_number = entry_card.get().strip()
        expiry = entry_expiry.get().strip()
        cvv = entry_cvv.get().strip()

        if not card_number or not expiry or not cvv:
            messagebox.showerror("Error", "All fields are required!")
            return

        if not card_number.isdigit() or len(card_number) not in (13, 16, 19):
            messagebox.showerror("Error", "Invalid card number.")
            return

        if not cvv.isdigit() or len(cvv) not in (3, 4):
            messagebox.showerror("Error", "Invalid CVV.")
            return

        save_card(username, card_number, expiry, cvv)
        messagebox.showinfo("Success", "Card added successfully!")
        card_window.destroy()

    def add_funds_to_card():
        cards = load_cards(username)
        if not cards:
            messagebox.showerror("Error", "No cards found. Add a card first.")
            return

        card_options = [f"{c['card_number']} (Balance: {c['balance']})" for c in cards]
        selected = simpledialog.askstring("Select Card", f"Available cards:\n" + "\n".join(card_options) + "\nEnter card number:")
        if not selected or selected not in [c["card_number"] for c in cards]:
            messagebox.showerror("Error", "Invalid card selection.")
            return

        amount = simpledialog.askfloat("Add Funds", "Enter amount to add:")
        if amount is None or amount <= 0:
            messagebox.showerror("Error", "Invalid amount.")
            return

        # Update balance
        for c in cards:
            if c["card_number"] == selected:
                new_balance = c["balance"] + amount
                update_card_balance(username, selected, new_balance)
                messagebox.showinfo("Success", f"Added {amount} to card {selected}. New balance: {new_balance}")
                break

    card_window = tk.Toplevel()
    card_window.title("Manage Cards")
    card_window.geometry("350x300")
    card_window.config(bg="#f0f8ff")

    tk.Label(card_window, text="Add New Card", font=("Arial", 12, "bold"), bg="#f0f8ff").pack(pady=10)
    tk.Label(card_window, text="Card Number:", bg="#f0f8ff").pack()
    entry_card = tk.Entry(card_window)
    entry_card.pack()
    tk.Label(card_window, text="Expiry Date (MM/YY):", bg="#f0f8ff").pack()
    entry_expiry = tk.Entry(card_window)
    entry_expiry.pack()
    tk.Label(card_window, text="CVV:", bg="#f0f8ff").pack()
    entry_cvv = tk.Entry(card_window, show="*")
    entry_cvv.pack()
    tk.Button(card_window, text="Add Card", command=save_new_card, bg="#90ee90", width=20).pack(pady=10)

    tk.Label(card_window, text="Or Manage Existing Cards", font=("Arial", 12, "bold"), bg="#f0f8ff").pack(pady=10)
    tk.Button(card_window, text="Add Funds", command=add_funds_to_card, bg="#add8e6", width=20).pack(pady=5)
