import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from card_details import load_cards, update_card_balance  # reuse existing functions

TRANSACTION_FILE = "transactions.txt"

def encrypt_string(s):
    # placeholder if encryption needed, reuse your existing encryption
    return s

def decrypt_string(s):
    # placeholder if encryption needed, reuse your existing encryption
    return s

def record_transaction(username, card_number, amount):
    """Record a transaction in the transactions file."""
    with open(TRANSACTION_FILE, "a") as f:
        f.write(f"{username},{card_number},{amount}\n")

def load_transactions(username):
    """Return all transactions for a user."""
    transactions = []
    if os.path.exists(TRANSACTION_FILE):
        with open(TRANSACTION_FILE, "r") as f:
            for line in f:
                user, card, amount = line.strip().split(",")
                if user == username:
                    transactions.append({"card_number": card, "amount": float(amount)})
    return transactions

def transaction_window(username):
    """Window to make transactions and see history."""
    trans_win = tk.Toplevel()
    trans_win.title("Transactions")
    trans_win.geometry("400x400")
    trans_win.config(bg="#f0f8ff")

    tk.Label(trans_win, text=f"Transactions for {username}", font=("Arial", 14, "bold"), bg="#f0f8ff").pack(pady=10)
    
    # TEXT widget for transaction history
    history_text = tk.Text(trans_win, height=15, width=45, state="disabled")
    history_text.pack(pady=10)

    def refresh_history():
        """Display the transaction history and card balances."""
        history_text.config(state="normal")
        history_text.delete(1.0, tk.END)
        transactions = load_transactions(username)
        cards = load_cards(username)

        history_text.insert(tk.END, f"Card Balances:\n")
        for c in cards:
            history_text.insert(tk.END, f"{c['card_number']}: {c['balance']}\n")

        history_text.insert(tk.END, "\nTransaction History:\n")
        if transactions:
            for t in transactions:
                history_text.insert(tk.END, f"Card {t['card_number']} - Spent: {t['amount']}\n")
        else:
            history_text.insert(tk.END, "No transactions yet.\n")
        history_text.config(state="disabled")

    def make_transaction():
        """Perform a transaction for a selected card."""
        cards = load_cards(username)
        if not cards:
            messagebox.showerror("Error", "No cards found. Add a card first.")
            return

        card_options = [f"{c['card_number']} (Balance: {c['balance']})" for c in cards]
        selected = simpledialog.askstring("Select Card", f"Available cards:\n" + "\n".join(card_options) + "\nEnter card number:")
        if not selected or selected not in [c["card_number"] for c in cards]:
            messagebox.showerror("Error", "Invalid card selection.")
            return

        amount = simpledialog.askfloat("Transaction Amount", "Enter amount to spend:")
        if amount is None or amount <= 0:
            messagebox.showerror("Error", "Invalid amount.")
            return

        # Update balance
        for c in cards:
            if c["card_number"] == selected:
                if c["balance"] < amount:
                    messagebox.showerror("Error", f"Insufficient funds. Current balance: {c['balance']}")
                    return
                new_balance = c["balance"] - amount
                update_card_balance(username, selected, new_balance)
                record_transaction(username, selected, amount)
                messagebox.showinfo("Success", f"Transaction successful!\nSpent: {amount}\nRemaining balance: {new_balance}")
                break

        refresh_history()  # update history after transaction

    # Buttons
    tk.Button(trans_win, text="Make Transaction", command=make_transaction, bg="#90ee90", width=20).pack(pady=10)

    # Initial load of history
    refresh_history()
