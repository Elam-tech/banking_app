import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import csv
from datetime import datetime
from calendar import monthrange
import base64
import os


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker with Savings")
        self.root.geometry("800x600")
        self.root.config(bg="#f0f8ff")

        # Data
        self.expenses = []
        self.initial_balance = 0.0
        self.remaining_balance = 0.0
        self.savings_balance = 0.0
        self.last_interest_date = datetime.now()
        self.selected_bank = None
        self.currency = ""
        self.savings_interest_rate = 0.02

        # Transaction log file
        self.transaction_file = "transactions.txt"

        # Bank data
        self.banks = [
            {"name": "JPMorgan Chase", "country": "USA", "currency": "USD", "interest_rate": 0.0425},
            {"name": "Bank of America", "country": "USA", "currency": "USD", "interest_rate": 0.0415},
            {"name": "HSBC", "country": "UK", "currency": "GBP", "interest_rate": 0.0385},
            {"name": "Barclays", "country": "UK", "currency": "GBP", "interest_rate": 0.0390},
            {"name": "Mitsubishi UFJ", "country": "Japan", "currency": "JPY", "interest_rate": 0.0025},
            {"name": "ICBC", "country": "China", "currency": "CNY", "interest_rate": 0.0275},
            {"name": "BNP Paribas", "country": "France", "currency": "EUR", "interest_rate": 0.0320},
            {"name": "Deutsche Bank", "country": "Germany", "currency": "EUR", "interest_rate": 0.0310},
            {"name": "Standard Bank", "country": "South Africa", "currency": "ZAR", "interest_rate": 0.0750},
            {"name": "First National Bank (FNB)", "country": "South Africa", "currency": "ZAR", "interest_rate": 0.0700},
            {"name": "ABSA Bank", "country": "South Africa", "currency": "ZAR", "interest_rate": 0.0685},
            {"name": "Nedbank", "country": "South Africa", "currency": "ZAR", "interest_rate": 0.0710},
            {"name": "Capitec Bank", "country": "South Africa", "currency": "ZAR", "interest_rate": 0.0695}
        ]

        # Select Bank
        bank_frame = tk.Frame(self.root, padx=10, pady=10, bg="#f0f8ff")
        bank_frame.pack(fill=tk.X)
        tk.Label(bank_frame, text="Select Bank:", bg="#f0f8ff").grid(row=0, column=0, sticky="w")
        self.bank_combo = ttk.Combobox(bank_frame, values=[b["name"] for b in self.banks])
        self.bank_combo.grid(row=0, column=1, padx=5)
        tk.Button(bank_frame, text="Set Bank", command=self.set_bank).grid(row=0, column=2, padx=5)

        # Input Frame
        input_frame = tk.Frame(self.root, padx=10, pady=10, bg="#f0f8ff")
        input_frame.pack(fill=tk.X)
        tk.Label(input_frame, text="Date (YYYY-MM-DD):", bg="#f0f8ff").grid(row=0, column=0, sticky="w")
        self.date_entry = tk.Entry(input_frame)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Category:", bg="#f0f8ff").grid(row=0, column=2, sticky="w")
        self.category_entry = tk.Entry(input_frame)
        self.category_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="Description:", bg="#f0f8ff").grid(row=1, column=0, sticky="w")
        self.desc_entry = tk.Entry(input_frame)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Amount:", bg="#f0f8ff").grid(row=1, column=2, sticky="w")
        self.amount_entry = tk.Entry(input_frame)
        self.amount_entry.grid(row=1, column=3, padx=5, pady=5)

        tk.Button(input_frame, text="Add Expense", command=self.add_expense, bg="#90ee90").grid(row=2, column=0, columnspan=4, pady=10)

        # Balance Frame
        balance_frame = tk.Frame(self.root, padx=10, pady=10, bg="#f0f8ff")
        balance_frame.pack(fill=tk.X)

        tk.Label(balance_frame, text="Initial Balance:", bg="#f0f8ff").grid(row=0, column=0, sticky="w")
        self.balance_entry = tk.Entry(balance_frame)
        self.balance_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(balance_frame, text="Set Balance", command=self.set_initial_balance, bg="#add8e6").grid(row=0, column=2, padx=5)

        tk.Label(balance_frame, text="Add Funds:", bg="#f0f8ff").grid(row=1, column=0, sticky="w")
        self.add_funds_entry = tk.Entry(balance_frame)
        self.add_funds_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(balance_frame, text="Add to Balance", command=self.add_funds, bg="#add8e6").grid(row=1, column=2, padx=5)

        tk.Label(balance_frame, text="Transfer to Savings:", bg="#f0f8ff").grid(row=2, column=0, sticky="w")
        self.to_savings_entry = tk.Entry(balance_frame)
        self.to_savings_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(balance_frame, text="Transfer", command=self.transfer_to_savings, bg="#add8e6").grid(row=2, column=2, padx=5)

        self.balance_label = tk.Label(balance_frame, text="Remaining Balance: 0.0", font=("Arial", 12, "bold"), bg="#f0f8ff")
        self.balance_label.grid(row=0, column=3, padx=20)
        self.savings_label = tk.Label(balance_frame, text="Savings Balance: 0.0", font=("Arial", 12, "bold"), bg="#f0f8ff")
        self.savings_label.grid(row=1, column=3, padx=20)

        tk.Button(balance_frame, text="Apply Monthly Interest", command=lambda: self.apply_monthly_interest(auto=False), bg="#ffb347").grid(row=2, column=3, padx=20)

        tk.Button(balance_frame, text="Projected Month-End Balance", command=self.calculate_projected_balance, bg="#ffa500").grid(row=3, column=0, columnspan=2, pady=10)

        # Table Frame
        table_frame = tk.Frame(self.root, bg="#f0f8ff")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("Date", "Category", "Description", "Amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Menu
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save to CSV", command=self.save_to_csv)
        file_menu.add_command(label="Load from CSV", command=self.load_from_csv)
        file_menu.add_command(label="Clear History", command=self.clear_history)
        file_menu.add_command(label="View Transactions", command=self.view_transactions)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

        # Apply automatic interest
        self.apply_monthly_interest(auto=True)

    # ===== ENCRYPTION HELPERS =====
    def encrypt_string(self, s: str) -> str:
        return base64.b64encode(s.encode("utf-8")).decode("utf-8")

    def decrypt_string(self, s: str) -> str:
        return base64.b64decode(s.encode("utf-8")).decode("utf-8")

    # ===== TRANSACTION LOG =====
    def record_transaction(self, trans_type: str, amount: float, details: str = ""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{trans_type},{amount},{details},{timestamp}"
        encrypted = self.encrypt_string(entry)

        with open(self.transaction_file, "a") as f:
            f.write(encrypted + "\n")

    def load_transactions(self):
        transactions = []
        if not os.path.exists(self.transaction_file):
            return transactions
        with open(self.transaction_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        decrypted = self.decrypt_string(line)
                        transactions.append(decrypted)
                    except Exception:
                        continue
        return transactions

    def view_transactions(self):
        transactions = self.load_transactions()
        if not transactions:
            messagebox.showinfo("Transactions", "No transactions found.")
            return
        history = "\n".join(transactions[-20:])  # show last 20
        messagebox.showinfo("Transaction History", history)

    # ===== BANK =====
    def set_bank(self):
        bank_name = self.bank_combo.get()
        for b in self.banks:
            if b["name"] == bank_name:
                self.selected_bank = b
                self.currency = b["currency"]
                self.savings_interest_rate = b["interest_rate"]
                messagebox.showinfo("Bank Set", f"Bank set to {bank_name} ({self.currency})\nInterest {self.savings_interest_rate*100:.2f}%")
                return
        messagebox.showerror("Error", "Please select a valid bank")

    # ===== EXPENSES =====
    def add_expense(self):
        date = self.date_entry.get()
        category = self.category_entry.get()
        description = self.desc_entry.get()
        amount = self.amount_entry.get()
        if not amount.replace('.', '', 1).isdigit():
            messagebox.showerror("Invalid Input", "Amount must be a number")
            return
        if date and category and description and amount:
            expense = (date, category, description, float(amount))
            self.expenses.append(expense)
            self.tree.insert("", tk.END, values=expense)
            self.remaining_balance -= float(amount)
            self.update_balance_labels()
            self.record_transaction("Expense", float(amount), f"{category}-{description}")
            self.category_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            if self.remaining_balance < 0:
                messagebox.showwarning("Warning", "Your balance is negative!")
        else:
            messagebox.showerror("Error", "Please fill in all fields")

    def set_initial_balance(self):
        balance = self.balance_entry.get()
        if not balance.replace('.', '', 1).isdigit():
            messagebox.showerror("Invalid Input", "Balance must be a number")
            return
        self.initial_balance = float(balance)
        self.remaining_balance = self.initial_balance - sum(exp[3] for exp in self.expenses)
        self.update_balance_labels()
        self.record_transaction("Initial Balance", self.initial_balance)
        messagebox.showinfo("Balance Set", f"Initial balance set to {self.initial_balance}")

    def add_funds(self):
        amount = self.add_funds_entry.get()
        if not amount.replace('.', '', 1).isdigit():
            messagebox.showerror("Invalid Input", "Amount must be a number")
            return
        self.remaining_balance += float(amount)
        self.update_balance_labels()
        self.record_transaction("Add Funds", float(amount))
        self.add_funds_entry.delete(0, tk.END)

    def transfer_to_savings(self):
        amount = self.to_savings_entry.get()
        if not amount.replace('.', '', 1).isdigit():
            messagebox.showerror("Invalid Input", "Amount must be a number")
            return
        amount = float(amount)
        if amount > self.remaining_balance:
            messagebox.showerror("Error", "Insufficient balance")
            return
        self.remaining_balance -= amount
        self.savings_balance += amount
        self.update_balance_labels()
        self.record_transaction("Transfer to Savings", amount)
        self.to_savings_entry.delete(0, tk.END)

    def apply_monthly_interest(self, auto=False):
        today = datetime.now()
        if auto:
            if (today - self.last_interest_date).days < 30:
                return
        interest = self.savings_balance * self.savings_interest_rate
        self.savings_balance += interest
        self.update_balance_labels()
        self.last_interest_date = today
        if interest > 0:
            self.record_transaction("Interest", interest)
        if not auto:
            messagebox.showinfo("Interest Applied", f"Added {round(interest,2)} {self.currency} to savings")

    def update_balance_labels(self):
        self.balance_label.config(text=f"Remaining Balance: {round(self.remaining_balance, 2)} {self.currency}")
        self.savings_label.config(text=f"Savings Balance: {round(self.savings_balance, 2)} {self.currency}")

    # ===== PROJECTIONS =====
    def calculate_projected_balance(self):
        if not self.expenses:
            messagebox.showinfo("Projected Balance", "No expenses recorded yet.")
            return
        today = datetime.now()
        year, month = today.year, today.month
        days_in_month = monthrange(year, month)[1]
        total_spent = sum(exp[3] for exp in self.expenses if datetime.strptime(exp[0], "%Y-%m-%d").month == month)
        days_passed = today.day
        avg_daily = total_spent / days_passed if days_passed > 0 else 0
        remaining_days = days_in_month - today.day
        projected = self.remaining_balance - (avg_daily * remaining_days)
        messagebox.showinfo("Projected Balance", f"Projected end balance: {projected:.2f} {self.currency}")

    # ===== CSV =====
    def save_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Date","Category","Description","Amount","InitialBalance","SavingsBalance","LastInterest"])
                for exp in self.expenses:
                    writer.writerow(list(exp) + [self.initial_balance, self.savings_balance, self.last_interest_date.isoformat()])
            messagebox.showinfo("Success", "Expenses saved!")

    def load_from_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.expenses.clear()
            self.tree.delete(*self.tree.get_children())
            with open(file_path, mode="r") as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    self.expenses.append((row[0], row[1], row[2], float(row[3])))
                    self.tree.insert("", tk.END, values=row[:4])
                    self.initial_balance = float(row[4])
                    self.savings_balance = float(row[5])
                    self.last_interest_date = datetime.fromisoformat(row[6])
            self.remaining_balance = self.initial_balance - sum(exp[3] for exp in self.expenses)
            self.update_balance_labels()
            self.apply_monthly_interest(auto=True)
            messagebox.showinfo("Success", "Expenses loaded!")

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure?"):
            self.expenses.clear()
            self.tree.delete(*self.tree.get_children())
            self.remaining_balance = self.initial_balance
            self.savings_balance = 0.0
            self.update_balance_labels()
            open(self.transaction_file, "w").close()  # clear transactions


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()


