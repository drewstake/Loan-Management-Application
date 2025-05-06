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

cols = ("CustomerID","Name","Phone", "Email", "SSN")
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

cols2 = ("LoanID","CustomerID","TypeID","Amount","Interest Rate", "Start Date", "End Date", "Status", "Date Approved", "Approved By","Amount Paid","Number Of Payments")
loan_tree = ttk.Treeview(tab2, columns=cols2, show="headings", height=6)
for c in cols2:
    loan_tree.heading(c, text=c)
loan_tree.pack(fill="x", padx=5, pady=5)

form2 = ttk.Frame(tab2); form2.pack(fill="x", pady=5)
ttk.Label(form2,text="LoanID:").grid(row=0,column=0);      ttk.Entry(form2,textvariable=loan_amount).grid(row=0,column=1)
ttk.Label(form2,text="CustomerID:").grid(row=1,column=0);     ttk.Entry(form2,textvariable=loan_rate).grid(row=1,column=1)
ttk.Label(form2,text="TypeID:").grid(row=2,column=0);       ttk.Entry(form2,textvariable=loan_type).grid(row=2,column=1)
ttk.Label(form2,text="Amount:").grid(row=3,column=0);    ttk.Entry(form2,textvariable=loan_cust_id).grid(row=3,column=1)
ttk.Label(form2,text="Interest:").grid(row=0,column=0);      ttk.Entry(form2,textvariable=loan_amount).grid(row=0,column=1)
ttk.Label(form2,text="Start Date:").grid(row=1,column=0);     ttk.Entry(form2,textvariable=loan_rate).grid(row=1,column=1)
ttk.Label(form2,text="End Date:").grid(row=2,column=0);       ttk.Entry(form2,textvariable=loan_type).grid(row=2,column=1)
ttk.Label(form2,text="Status:").grid(row=3,column=0);    ttk.Entry(form2,textvariable=loan_cust_id).grid(row=3,column=1)
ttk.Label(form2,text="Date Approved:").grid(row=1,column=0);     ttk.Entry(form2,textvariable=loan_rate).grid(row=1,column=1)
ttk.Label(form2,text="Approved By:").grid(row=2,column=0);       ttk.Entry(form2,textvariable=loan_type).grid(row=2,column=1)
ttk.Label(form2,text="Amount Paid:").grid(row=3,column=0);    ttk.Entry(form2,textvariable=loan_cust_id).grid(row=3,column=1)
ttk.Label(form2,text="Number Of Payments:").grid(row=1,column=0);     ttk.Entry(form2,textvariable=loan_rate).grid(row=1,column=1)

btns2 = ttk.Frame(tab2); btns2.pack(pady=5)
ttk.Button(btns2, text="Add",    command=add_loan).grid(row=0,column=0,padx=3)
ttk.Button(btns2, text="Update", command=update_loan).grid(row=0,column=1,padx=3)
ttk.Button(btns2, text="Delete", command=delete_loan).grid(row=0,column=2,padx=3)

refresh_loans()

# -- Mortgage View Tab --
tab3 = ttk.Frame(nb); nb.add(tab3, text="Mortgage")
loan_amount, loan_rate, loan_type, loan_cust_id, loan_search = (
    tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
)

frm2 = ttk.Frame(tab3); frm2.pack(fill="x", pady=2)
ttk.Entry(frm2, textvariable=loan_search).pack(side="left", padx=5)
ttk.Button(frm2, text="Search", command=lambda: refresh_loans(loan_search.get())).pack(side="left")
ttk.Button(frm2, text="Show All", command=lambda: refresh_loans("")).pack(side="left")

cols2 = ("LoanID","House Address","House Area","Bedrooms","House Price")
loan_tree = ttk.Treeview(tab3, columns=cols2, show="headings", height=6)
for c in cols2:
    loan_tree.heading(c, text=c)
loan_tree.pack(fill="x", padx=5, pady=5)

form2 = ttk.Frame(tab3); form2.pack(fill="x", pady=5)
ttk.Label(form2,text="LoanID:").grid(row=0,column=0);      ttk.Entry(form2,textvariable=loan_amount).grid(row=0,column=1)
ttk.Label(form2,text="House Address:").grid(row=1,column=0);     ttk.Entry(form2,textvariable=loan_rate).grid(row=1,column=1)
ttk.Label(form2,text="House Area:").grid(row=2,column=0);       ttk.Entry(form2,textvariable=loan_type).grid(row=2,column=1)
ttk.Label(form2,text="Bedrooms:").grid(row=3,column=0);    ttk.Entry(form2,textvariable=loan_cust_id).grid(row=3,column=1)
ttk.Label(form2,text="House Price:").grid(row=0,column=0);      ttk.Entry(form2,textvariable=loan_amount).grid(row=0,column=1)



# -- Auto View Tab --
tab4 = ttk.Frame(nb); nb.add(tab4, text="Auto")
loan_amount, loan_rate, loan_type, loan_cust_id, loan_search = (
    tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
)

frm2 = ttk.Frame(tab4); frm2.pack(fill="x", pady=2)
ttk.Entry(frm2, textvariable=loan_search).pack(side="left", padx=5)
ttk.Button(frm2, text="Search", command=lambda: refresh_loans(loan_search.get())).pack(side="left")
ttk.Button(frm2, text="Show All", command=lambda: refresh_loans("")).pack(side="left")

cols2 = ("LoanID","CustomerID","TypeID","Amount","Interest Rate", "Start Date", "End Date", "Status", "Date Approved", "Approved By","Amount Paid","Number Of Payments")
loan_tree = ttk.Treeview(tab4, columns=cols2, show="headings", height=6)
for c in cols2:
    loan_tree.heading(c, text=c)
loan_tree.pack(fill="x", padx=5, pady=5)

form2 = ttk.Frame(tab4); form2.pack(fill="x", pady=5)
ttk.Label(form2,text="LoanID:").grid(row=0,column=0);      ttk.Entry(form2,textvariable=loan_amount).grid(row=0,column=1)
ttk.Label(form2,text="Make:").grid(row=1,column=0);     ttk.Entry(form2,textvariable=loan_rate).grid(row=1,column=1)
ttk.Label(form2,text="Model:").grid(row=2,column=0);       ttk.Entry(form2,textvariable=loan_type).grid(row=2,column=1)
ttk.Label(form2,text="Year:").grid(row=3,column=0);    ttk.Entry(form2,textvariable=loan_cust_id).grid(row=3,column=1)
ttk.Label(form2,text="VIN:").grid(row=0,column=0);      ttk.Entry(form2,textvariable=loan_amount).grid(row=0,column=1)

# -- Personal View Tab --
tab5 = ttk.Frame(nb); nb.add(tab5, text="Personal")
loan_amount, loan_rate, loan_type, loan_cust_id, loan_search = (
    tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
)

frm2 = ttk.Frame(tab5); frm2.pack(fill="x", pady=2)
ttk.Entry(frm2, textvariable=loan_search).pack(side="left", padx=5)
ttk.Button(frm2, text="Search", command=lambda: refresh_loans(loan_search.get())).pack(side="left")
ttk.Button(frm2, text="Show All", command=lambda: refresh_loans("")).pack(side="left")

cols2 = ("LoanID","CustomerID","TypeID","Amount","Interest Rate", "Start Date", "End Date", "Status", "Date Approved", "Approved By","Amount Paid","Number Of Payments")
loan_tree = ttk.Treeview(tab4, columns=cols2, show="headings", height=6)
for c in cols2:
    loan_tree.heading(c, text=c)
loan_tree.pack(fill="x", padx=5, pady=5)

form2 = ttk.Frame(tab5); form2.pack(fill="x", pady=5)
ttk.Label(form2,text="LoanID:").grid(row=0,column=0);      ttk.Entry(form2,textvariable=loan_amount).grid(row=0,column=1)
ttk.Label(form2,text="Purpose:").grid(row=1,column=0);     ttk.Entry(form2,textvariable=loan_rate).grid(row=1,column=1)


# -- Student View Tab --
tab6 = ttk.Frame(nb); nb.add(tab6, text="Student")
loan_amount, loan_rate, loan_type, loan_cust_id, loan_search = (
    tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
)

frm2 = ttk.Frame(tab6); frm2.pack(fill="x", pady=2)
ttk.Entry(frm2, textvariable=loan_search).pack(side="left", padx=5)
ttk.Button(frm2, text="Search", command=lambda: refresh_loans(loan_search.get())).pack(side="left")
ttk.Button(frm2, text="Show All", command=lambda: refresh_loans("")).pack(side="left")

cols2 = ("LoanID","CustomerID","TypeID","Amount","Interest Rate", "Start Date", "End Date", "Status", "Date Approved", "Approved By","Amount Paid","Number Of Payments")
loan_tree = ttk.Treeview(tab4, columns=cols2, show="headings", height=6)
for c in cols2:
    loan_tree.heading(c, text=c)
loan_tree.pack(fill="x", padx=5, pady=5)

form2 = ttk.Frame(tab6); form2.pack(fill="x", pady=5)
ttk.Label(form2,text="LoanID:").grid(row=0,column=0);      ttk.Entry(form2,textvariable=loan_amount).grid(row=0,column=1)
ttk.Label(form2,text="Disbursement Date:").grid(row=1,column=0);     ttk.Entry(form2,textvariable=loan_rate).grid(row=1,column=1)
ttk.Label(form2,text="Repayment Start:").grid(row=2,column=0);       ttk.Entry(form2,textvariable=loan_type).grid(row=2,column=1)
ttk.Label(form2,text="Repayment End:").grid(row=3,column=0);    ttk.Entry(form2,textvariable=loan_cust_id).grid(row=3,column=1)
ttk.Label(form2,text="Monthly:").grid(row=0,column=0);      ttk.Entry(form2,textvariable=loan_amount).grid(row=0,column=1)
ttk.Label(form2,text="Grace Period:").grid(row=1,column=0);     ttk.Entry(form2,textvariable=loan_rate).grid(row=1,column=1)

# ----- STARTUP -----
init_db()
init_db()
app.mainloop()
