import tkinter as tk
from tkinter import messagebox
import sqlite3

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect("loans.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Customer (
                    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    IncomeProof TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Staff (
                    StaffID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    Role TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS Loan (
                    LoanID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Amount REAL NOT NULL,
                    InterestRate REAL NOT NULL,
                    LoanType TEXT NOT NULL,
                    CustomerID INTEGER,
                    StaffID INTEGER,
                    FOREIGN KEY(CustomerID) REFERENCES Customer(CustomerID),
                    FOREIGN KEY(StaffID) REFERENCES Staff(StaffID))''')
    conn.commit()
    conn.close()

# ---------- GUI FUNCTIONS ----------
def add_customer():
    name = name_entry.get()
    income = income_entry.get()
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
        messagebox.showwarning("Input Error", "Please enter all fields")

def add_loan():
    try:
        amount = float(amount_entry.get())
        rate = float(rate_entry.get())
        loan_type = loan_type_entry.get()
        cust_id = int(customer_id_entry.get())
        staff_id = int(staff_id_entry.get())
        
        conn = sqlite3.connect("loans.db")
        c = conn.cursor()
        c.execute("INSERT INTO Loan (Amount, InterestRate, LoanType, CustomerID, StaffID) VALUES (?, ?, ?, ?, ?)",
                  (amount, rate, loan_type, cust_id, staff_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Loan added successfully")
        amount_entry.delete(0, tk.END)
        rate_entry.delete(0, tk.END)
        loan_type_entry.delete(0, tk.END)
        customer_id_entry.delete(0, tk.END)
        staff_id_entry.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add loan: {e}")

# ---------- GUI SETUP ----------
app = tk.Tk()
app.title("Loan Management System")

# Customer Section
tk.Label(app, text="Customer Name").grid(row=0, column=0)
name_entry = tk.Entry(app)
name_entry.grid(row=0, column=1)

tk.Label(app, text="Income Proof").grid(row=1, column=0)
income_entry = tk.Entry(app)
income_entry.grid(row=1, column=1)

tk.Button(app, text="Add Customer", command=add_customer).grid(row=2, column=1)

# Loan Section
tk.Label(app, text="Loan Amount").grid(row=3, column=0)
amount_entry = tk.Entry(app)
amount_entry.grid(row=3, column=1)

tk.Label(app, text="Interest Rate (%)").grid(row=4, column=0)
rate_entry = tk.Entry(app)
rate_entry.grid(row=4, column=1)

tk.Label(app, text="Loan Type").grid(row=5, column=0)
loan_type_entry = tk.Entry(app)
loan_type_entry.grid(row=5, column=1)

tk.Label(app, text="Customer ID").grid(row=6, column=0)
customer_id_entry = tk.Entry(app)
customer_id_entry.grid(row=6, column=1)

tk.Label(app, text="Staff ID").grid(row=7, column=0)
staff_id_entry = tk.Entry(app)
staff_id_entry.grid(row=7, column=1)

tk.Button(app, text="Add Loan", command=add_loan).grid(row=8, column=1)

init_db()
app.mainloop()
