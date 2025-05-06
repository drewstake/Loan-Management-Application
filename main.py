import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect("loans.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS Customer (
            CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            IncomeProof TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Staff (
            StaffID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Role TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Loan (
            LoanID INTEGER PRIMARY KEY AUTOINCREMENT,
            Amount REAL NOT NULL,
            InterestRate REAL NOT NULL,
            LoanType TEXT NOT NULL,
            CustomerID INTEGER,
            StaffID INTEGER,
            FOREIGN KEY(CustomerID) REFERENCES Customer(CustomerID),
            FOREIGN KEY(StaffID) REFERENCES Staff(StaffID)
        )
    ''')
    conn.commit()
    conn.close()

# ---------- GUI FUNCTIONS ----------
def add_customer():
    name = name_entry.get().strip()
    income = income_entry.get().strip()
    if name and income:
        conn = sqlite3.connect("loans.db")
        c = conn.cursor()
        c.execute("INSERT INTO Customer (Name, IncomeProof) VALUES (?, ?)", (name, income))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Customer added successfully")
        name_entry.delete(0, tk.END)
        income_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please enter both Name and Income Proof")

def add_loan():
    try:
        amount    = float(amount_entry.get())
        rate      = float(rate_entry.get())
        loan_type = loan_type_entry.get().strip()
        cust_id   = int(customer_id_entry.get())
        staff_id  = int(staff_id_entry.get())
        conn = sqlite3.connect("loans.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO Loan 
            (Amount, InterestRate, LoanType, CustomerID, StaffID)
            VALUES (?, ?, ?, ?, ?)
        """, (amount, rate, loan_type, cust_id, staff_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Loan added successfully")
        # clear inputs
        amount_entry.delete(0, tk.END)
        rate_entry.delete(0, tk.END)
        loan_type_entry.delete(0, tk.END)
        customer_id_entry.delete(0, tk.END)
        staff_id_entry.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add loan:\n{e}")

def view_loans():
    # clear existing rows
    for row in loan_tree.get_children():
        loan_tree.delete(row)
    conn = sqlite3.connect("loans.db")
    c = conn.cursor()
    c.execute("SELECT * FROM Loan")
    for record in c.fetchall():
        loan_tree.insert("", tk.END, values=record)
    conn.close()

def delete_loan():
    selected = loan_tree.selection()
    if not selected:
        messagebox.showwarning("No selection", "Please select a loan to delete")
        return
    loan_id = loan_tree.item(selected[0])['values'][0]
    conn = sqlite3.connect("loans.db")
    c = conn.cursor()
    c.execute("DELETE FROM Loan WHERE LoanID = ?", (loan_id,))
    conn.commit()
    conn.close()
    view_loans()
    messagebox.showinfo("Deleted", f"Loan ID {loan_id} has been deleted")

# ---------- GUI SETUP ----------
app = tk.Tk()
app.title("Loan Management System")

# Customer entry
tk.Label(app, text="Customer Name:").grid(row=0, column=0, sticky="e")
name_entry = tk.Entry(app)
name_entry.grid(row=0, column=1, padx=5, pady=2)

tk.Label(app, text="Income Proof:").grid(row=1, column=0, sticky="e")
income_entry = tk.Entry(app)
income_entry.grid(row=1, column=1, padx=5, pady=2)

tk.Button(app, text="Add Customer", command=add_customer).grid(row=2, column=1, pady=5, sticky="e")

# Loan entry
tk.Label(app, text="Loan Amount:").grid(row=3, column=0, sticky="e")
amount_entry = tk.Entry(app)
amount_entry.grid(row=3, column=1, padx=5, pady=2)

tk.Label(app, text="Interest Rate (%):").grid(row=4, column=0, sticky="e")
rate_entry = tk.Entry(app)
rate_entry.grid(row=4, column=1, padx=5, pady=2)

tk.Label(app, text="Loan Type:").grid(row=5, column=0, sticky="e")
loan_type_entry = tk.Entry(app)
loan_type_entry.grid(row=5, column=1, padx=5, pady=2)

tk.Label(app, text="Customer ID:").grid(row=6, column=0, sticky="e")
customer_id_entry = tk.Entry(app)
customer_id_entry.grid(row=6, column=1, padx=5, pady=2)

tk.Label(app, text="Staff ID:").grid(row=7, column=0, sticky="e")
staff_id_entry = tk.Entry(app)
staff_id_entry.grid(row=7, column=1, padx=5, pady=2)

tk.Button(app, text="Add Loan", command=add_loan).grid(row=8, column=1, pady=5, sticky="e")

# View & Delete section
tk.Button(app, text="View Loans", command=view_loans).grid(row=9, column=0, pady=5)
tk.Button(app, text="Delete Selected Loan", command=delete_loan).grid(row=9, column=1, pady=5)

# Treeview for displaying loans
columns = ("LoanID", "Amount", "InterestRate", "LoanType", "CustomerID", "StaffID")
loan_tree = ttk.Treeview(app, columns=columns, show="headings", height=8)
for col in columns:
    loan_tree.heading(col, text=col)
    loan_tree.column(col, width=100, anchor="center")
loan_tree.grid(row=10, column=0, columnspan=2, padx=5, pady=10)

# Initialize database & start GUI loop
init_db()
app.mainloop()
