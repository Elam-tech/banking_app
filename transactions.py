import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from datetime import datetime
from card_details import load_cards, update_card_balance  # existing functions

TRANSACTION_FILE = "transactions.txt"

# --- Encryption helpers ---
def encrypt_string(s: str) -> str:
    return "".join(chr(ord(c) + 3) for c in s)  # Caesar cipher placeholder

def decrypt_string(s: str) -> str:
    return "".join(chr(ord(c) - 3) for c in s)


# --- Transaction helpers ---
def record_transaction(username, card_number, description, amount, balance_after):
    """Save a transaction securely."""
    with open(TRANSACTION_FILE, "a") as f:
        line = f"{username},{card_number},{description},{amount},{balance_after},{datetime.now()}\n"
        f.write(encrypt_string(line))


def load_transactions(username):
    """Load all decrypted transactions for a user."""
    transactions = []
    if os.path.exists(TRANSACTION_FILE):
        with open(TRANSACTION_FILE, "r") as f:
            for line in f:
                try:
                    user, card, desc, amount, balance, date_str = decrypt_string(line.strip()).split(",")
                    if user == username:
                        transactions.append({
                            "card_number": card,
                            "description": desc,
                            "amount": float(amount),
                            "balance": float(balance),
                            "date": date_str
                        })
                except Exception:
                    continue
    return transactions


def censor_card_number(card_number):
    """Show only last 4 digits of a card number."""
    return "**** **** **** " + card_number[-4:]


# --- Transaction Window ---
def transaction_window(username):
    """Main window for transactions."""
    trans_win = tk.Toplevel()
    trans_win.title("Transactions")
    trans_win.geometry("500x500")
    trans_win.config(bg="#f0f8ff")

    tk.Label(trans_win, text=f"Transactions for {username}",
             font=("Arial", 14, "bold"), bg="#f0f8ff").pack(pady=10)

    history_text = tk.Text(trans_win, height=20, width=60, state="disabled")
    history_text.pack(pady=10)

    def refresh_history():
        """Update balances & transactions display."""
        history_text.config(state="normal")
        history_text.delete(1.0, tk.END)

        cards = load_cards(username)
        history_text.insert(tk.END, "Card Balances:\n")
        for c in cards:
            history_text.insert(tk.END, f"{censor_card_number(c['card_number'])}: {c['balance']}\n")

        history_text.insert(tk.END, "\nTransaction History:\n")
        transactions = load_transactions(username)
        if transactions:
            for t in transactions:
                history_text.insert(
                    tk.END,
                    f"{t['date']} | {censor_card_number(t['card_number'])} | {t['description']} | Amount: {t['amount']} | Balance: {t['balance']}\n"
                )
        else:
            history_text.insert(tk.END, "No transactions yet.\n")

        history_text.config(state="disabled")

    def make_transaction():
        """Spend money on a selected card."""
        cards = load_cards(username)
        if not cards:
            messagebox.showerror("Error", "No cards found. Add a card first.")
            return

        selected = simpledialog.askstring(
            "Select Card",
            "Available cards:\n" + "\n".join([censor_card_number(c["card_number"]) for c in cards]) +
            "\nEnter last 4 digits:"
        )
        chosen_card = None
        for c in cards:
            if c["card_number"][-4:] == selected:
                chosen_card = c
                break
        if not chosen_card:
            messagebox.showerror("Error", "Invalid card selection.")
            return

        amount = simpledialog.askfloat("Transaction Amount", "Enter amount to spend:")
        if amount is None or amount <= 0:
            messagebox.showerror("Error", "Invalid amount.")
            return
        if chosen_card["balance"] < amount:
            messagebox.showerror("Error", "Insufficient funds.")
            return

        new_balance = chosen_card["balance"] - amount
        update_card_balance(username, chosen_card["card_number"], new_balance)
        record_transaction(username, chosen_card["card_number"], "Purchase", amount, new_balance)

        messagebox.showinfo("Success", f"Transaction successful!\nSpent: {amount}\nRemaining balance: {new_balance}")
        refresh_history()

    def send_money():
        """Send money to another user."""
        cards = load_cards(username)
        if not cards:
            messagebox.showerror("Error", "No cards available.")
            return

        # Select sender card
        selected = simpledialog.askstring(
            "Select Card",
            "Your cards:\n" + "\n".join([censor_card_number(c['card_number']) for c in cards]) +
            "\nEnter last 4 digits:"
        )
        sender_card = None
        for c in cards:
            if c["card_number"][-4:] == selected:
                sender_card = c
                break
        if not sender_card:
            messagebox.showerror("Error", "Invalid card selection.")
            return

        # Verify CVV
        cvv_input = simpledialog.askstring("CVV", "Enter CVV to authorize transfer:", show="*")
        if cvv_input != sender_card["cvv"]:
            messagebox.showerror("Error", "Incorrect CVV.")
            return

        # Enter recipient
        recipient = simpledialog.askstring("Recipient", "Enter recipient username:")
        if not recipient:
            return

        recipient_cards = load_cards(recipient)
        if not recipient_cards:
            messagebox.showerror("Error", f"Recipient '{recipient}' has no cards.")
            return

        # Enter amount
        amount = simpledialog.askfloat("Amount", "Enter amount to send:")
        if amount is None or amount <= 0:
            return
        if sender_card["balance"] < amount:
            messagebox.showerror("Error", "Insufficient funds.")
            return

        # Deduct from sender
        new_sender_balance = sender_card["balance"] - amount
        update_card_balance(username, sender_card["card_number"], new_sender_balance)
        record_transaction(username, sender_card["card_number"], f"Sent to {recipient}", amount, new_sender_balance)

        # Credit recipient (first card for now)
        recipient_card = recipient_cards[0]
        new_recipient_balance = recipient_card["balance"] + amount
        update_card_balance(recipient, recipient_card["card_number"], new_recipient_balance)
        record_transaction(recipient, recipient_card["card_number"], f"Received from {username}", amount, new_recipient_balance)

        messagebox.showinfo("Success", f"Sent {amount} to {recipient}!")
        refresh_history()

    # Buttons
    tk.Button(trans_win, text="Make Transaction", command=make_transaction,
              bg="#90ee90", width=20).pack(pady=5)
    tk.Button(trans_win, text="Send Money", command=send_money,
              bg="#87cefa", width=20).pack(pady=5)

    refresh_history()

