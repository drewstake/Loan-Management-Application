import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ----- DATABASE SETUP -----
def init_db():
    conn = sqlite3.connect("loans.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS Customer (
            CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            IncomeProof TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS Loan (
            LoanID INTEGER PRIMARY KEY AUTOINCREMENT,
            Amount REAL NOT NULL,
            InterestRate REAL NOT NULL,
            LoanType TEXT NOT NULL,
            CustomerID INTEGER NOT NULL,
            FOREIGN KEY(CustomerID) REFERENCES Customer(CustomerID)
        )
    """)
    conn.commit()
    conn.close()

# ----- CUSTOMER CRUD -----
def refresh_customers(search_term=""):
    for row in cust_tree.get_children():
        cust_tree.delete(row)
    conn = sqlite3.connect("loans.db")
    c = conn.cursor()
    if search_term.strip():
        c.execute("SELECT * FROM Customer WHERE Name LIKE ? OR CustomerID = ?",
                  (f"%{search_term}%", search_term if search_term.isdigit() else -1))
    else:
        c.execute("SELECT * FROM Customer")
    for record in c.fetchall():
        cust_tree.insert("", tk.END, values=record)
    conn.close()

def add_customer():
    n = cust_name.get().strip()
    ip = cust_income.get().strip()
    if not n or not ip:
        messagebox.showwarning("Input error", "Name & Income Proof required")
        return
    conn = sqlite3.connect("loans.db")
    c = conn.cursor()
    c.execute("INSERT INTO Customer (Name, IncomeProof) VALUES (?, ?)", (n, ip))
    conn.commit(); conn.close()
    cust_name.set(""); cust_income.set("")
    refresh_customers()

def update_customer():
    sel = cust_tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Select a customer to edit")
        return
    cid = cust_tree.item(sel[0])['values'][0]
    n = cust_name.get().strip()
    ip = cust_income.get().strip()
    if not n or not ip:
        messagebox.showwarning("Input error", "Name & Income Proof required")
        return
    conn = sqlite3.connect("loans.db")
    c = conn.cursor()
    c.execute("UPDATE Customer SET Name=?, IncomeProof=? WHERE CustomerID=?", (n, ip, cid))
    conn.commit(); conn.close()
    cust_name.set(""); cust_income.set("")
    refresh_customers()

def delete_customer():
    sel = cust_tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Select a customer to delete")
        return
    cid = cust_tree.item(sel[0])['values'][0]
    if messagebox.askyesno("Confirm", f"Delete Customer {cid}?"):
        conn = sqlite3.connect("loans.db")
        c = conn.cursor()
        c.execute("DELETE FROM Customer WHERE CustomerID=?", (cid,))
        conn.commit(); conn.close()
        refresh_customers()

# ----- LOAN CRUD -----
def refresh_loans(search_term=""):
    for row in loan_tree.get_children():
        loan_tree.delete(row)
    conn = sqlite3.connect("loans.db")
    c = conn.cursor()
    if search_term.strip():
        if search_term.isdigit():
            c.execute("SELECT * FROM Loan WHERE LoanID=? OR CustomerID=?", (int(search_term), int(search_term)))
        else:
            c.execute("SELECT * FROM Loan WHERE LoanType LIKE ?", (f"%{search_term}%",))
    else:
        c.execute("SELECT * FROM Loan")
    for record in c.fetchall():
        loan_tree.insert("", tk.END, values=record)
    conn.close()

def add_loan():
    try:
        amt = float(loan_amount.get())
        rate = float(loan_rate.get())
        lt  = loan_type.get().strip()
        cid = int(loan_cust_id.get())
    except:
        messagebox.showwarning("Input error", "Check loan fields & Customer ID")
        return
    conn = sqlite3.connect("loans.db")
    c = conn.cursor()
    c.execute("""INSERT INTO Loan
                 (Amount, InterestRate, LoanType, CustomerID)
                 VALUES (?, ?, ?, ?)""",
              (amt, rate, lt, cid))
    conn.commit(); conn.close()
    loan_amount.set(""); loan_rate.set(""); loan_type .set(""); loan_cust_id.set("")
    refresh_loans()

def update_loan():
    sel = loan_tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Select a loan to edit")
        return
    lid = loan_tree.item(sel[0])['values'][0]
    try:
        amt = float(loan_amount.get())
        rate = float(loan_rate.get())
        lt  = loan_type.get().strip()
        cid = int(loan_cust_id.get())
    except:
        messagebox.showwarning("Input error", "Check loan fields & Customer ID")
        return
    conn = sqlite3.connect("loans.db")
    c = conn.cursor()
    c.execute("""UPDATE Loan
                 SET Amount=?, InterestRate=?, LoanType=?, CustomerID=?
                 WHERE LoanID=?""",
              (amt, rate, lt, cid, lid))
    conn.commit(); conn.close()
    loan_amount.set(""); loan_rate.set(""); loan_type.set(""); loan_cust_id.set("")
    refresh_loans()

def delete_loan():
    sel = loan_tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Select a loan to delete")
        return
    lid = loan_tree.item(sel[0])['values'][0]
    if messagebox.askyesno("Confirm", f"Delete Loan {lid}?"):
        conn = sqlite3.connect("loans.db")
        c = conn.cursor()
        c.execute("DELETE FROM Loan WHERE LoanID=?", (lid,))
        conn.commit(); conn.close()
        refresh_loans()

# ----- CUSTOMER VIEW -----
def view_customer_loans():
    for row in view_tree.get_children():
        view_tree.delete(row)
    try:
        cid = int(view_cust_id.get())
    except:
        messagebox.showwarning("Input error", "Enter a valid Customer ID")
        return
    conn = sqlite3.connect("loans.db")
    c = conn.cursor()
    c.execute("SELECT * FROM Loan WHERE CustomerID=?", (cid,))
    rows = c.fetchall()
    conn.close()
    for r in rows:
        view_tree.insert("", tk.END, values=r)

# ----- UI LAYOUT -----
app = tk.Tk()
app.title("Loan Management System")
nb = ttk.Notebook(app)
nb.pack(fill="both", expand=True, padx=5, pady=5)

# -- Customers Tab --
tab1 = ttk.Frame(nb); nb.add(tab1, text="Customers")
cust_name, cust_income, cust_search = tk.StringVar(), tk.StringVar(), tk.StringVar()

frm = ttk.Frame(tab1); frm.pack(fill="x", pady=2)
ttk.Entry(frm, textvariable=cust_search).pack(side="left", padx=5)
ttk.Button(frm, text="Search", command=lambda: refresh_customers(cust_search.get())).pack(side="left")
ttk.Button(frm, text="Show All", command=lambda: refresh_customers("")).pack(side="left")

cols = ("CustomerID","Name","IncomeProof")
cust_tree = ttk.Treeview(tab1, columns=cols, show="headings", height=6)
for c in cols:
    cust_tree.heading(c, text=c)
cust_tree.pack(fill="x", padx=5, pady=5)

form = ttk.Frame(tab1); form.pack(fill="x", pady=5)
ttk.Label(form,text="Name:").grid(row=0,column=0); ttk.Entry(form, textvariable=cust_name).grid(row=0,column=1)
ttk.Label(form,text="Income Proof:").grid(row=1,column=0); ttk.Entry(form, textvariable=cust_income).grid(row=1,column=1)
btns = ttk.Frame(tab1); btns.pack(pady=5)
ttk.Button(btns, text="Add",    command=add_customer).grid(row=0,column=0,padx=3)
ttk.Button(btns, text="Update", command=update_customer).grid(row=0,column=1,padx=3)
ttk.Button(btns, text="Delete", command=delete_customer).grid(row=0,column=2,padx=3)

refresh_customers()

# -- Loans Tab --
tab2 = ttk.Frame(nb); nb.add(tab2, text="Loans")
loan_amount, loan_rate, loan_type, loan_cust_id, loan_search = (
    tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
)

frm2 = ttk.Frame(tab2); frm2.pack(fill="x", pady=2)
ttk.Entry(frm2, textvariable=loan_search).pack(side="left", padx=5)
ttk.Button(frm2, text="Search", command=lambda: refresh_loans(loan_search.get())).pack(side="left")
ttk.Button(frm2, text="Show All", command=lambda: refresh_loans("")).pack(side="left")

cols2 = ("LoanID","Amount","InterestRate","LoanType","CustomerID")
loan_tree = ttk.Treeview(tab2, columns=cols2, show="headings", height=6)
for c in cols2:
    loan_tree.heading(c, text=c)
loan_tree.pack(fill="x", padx=5, pady=5)

form2 = ttk.Frame(tab2); form2.pack(fill="x", pady=5)
ttk.Label(form2,text="Amount:").grid(row=0,column=0);      ttk.Entry(form2,textvariable=loan_amount).grid(row=0,column=1)
ttk.Label(form2,text="Rate %:").grid(row=1,column=0);     ttk.Entry(form2,textvariable=loan_rate).grid(row=1,column=1)
ttk.Label(form2,text="Type:").grid(row=2,column=0);       ttk.Entry(form2,textvariable=loan_type).grid(row=2,column=1)
ttk.Label(form2,text="Cust ID:").grid(row=3,column=0);    ttk.Entry(form2,textvariable=loan_cust_id).grid(row=3,column=1)
btns2 = ttk.Frame(tab2); btns2.pack(pady=5)
ttk.Button(btns2, text="Add",    command=add_loan).grid(row=0,column=0,padx=3)
ttk.Button(btns2, text="Update", command=update_loan).grid(row=0,column=1,padx=3)
ttk.Button(btns2, text="Delete", command=delete_loan).grid(row=0,column=2,padx=3)

refresh_loans()

# -- Customer View Tab --
tab3 = ttk.Frame(nb); nb.add(tab3, text="View Customer Loans")
view_cust_id = tk.StringVar()
frm3 = ttk.Frame(tab3); frm3.pack(fill="x", pady=5)
ttk.Label(frm3, text="Customer ID:").pack(side="left", padx=5)
ttk.Entry(frm3, textvariable=view_cust_id, width=10).pack(side="left")
ttk.Button(frm3, text="View Loans", command=view_customer_loans).pack(side="left", padx=5)

cols3 = cols2
view_tree = ttk.Treeview(tab3, columns=cols3, show="headings", height=8)
for c in cols3:
    view_tree.heading(c, text=c)
view_tree.pack(fill="both", expand=True, padx=5, pady=5)

# ----- STARTUP -----
init_db()
app.mainloop()
