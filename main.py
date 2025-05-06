import tkinter as tk
from tkinter import ttk, messagebox
import oracledb

# ---- Oracle connection helper ----
def get_connection():
    return oracledb.connect(
        user="loan_app",
        password="LoanPwd1",
        dsn="localhost:1521/XEPDB1"
    )

# ----- CUSTOMER CRUD -----
def refresh_customers(search_term=""):
    cust_tree.delete(*cust_tree.get_children())
    conn = get_connection(); cur = conn.cursor()
    if search_term.strip():
        try:
            cid = int(search_term)
        except ValueError:
            cid = -1
        cur.execute("""
            SELECT customer_id,
                   first_name || ' ' || last_name AS full_name,
                   phone
              FROM customers
             WHERE LOWER(first_name||' '||last_name) LIKE :1
                OR customer_id = :2
        """, (f"%{search_term.lower()}%", cid))
    else:
        cur.execute("""
            SELECT customer_id,
                   first_name || ' ' || last_name AS full_name,
                   phone
              FROM customers
        """)
    for row in cur:
        cust_tree.insert("", tk.END, values=row)
    conn.close()

def add_customer():
    name = cust_name.get().strip()
    ph   = cust_phone.get().strip()
    if not name or not ph:
        messagebox.showwarning("Input error", "Name & Phone required")
        return
    first, last = (name.split(" ",1) + [""])[:2]
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO customers(first_name, last_name, phone)
        VALUES(:1, :2, :3)
    """, (first, last, ph))
    conn.commit(); conn.close()
    cust_name.set(""); cust_phone.set("")
    refresh_customers()

def update_customer():
    sel = cust_tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Select a customer to edit")
        return
    cid = cust_tree.item(sel[0])['values'][0]
    name = cust_name.get().strip()
    ph   = cust_phone.get().strip()
    if not name or not ph:
        messagebox.showwarning("Input error", "Name & Phone required")
        return
    first, last = (name.split(" ",1) + [""])[:2]
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE customers
           SET first_name = :1,
               last_name  = :2,
               phone      = :3
         WHERE customer_id = :4
    """, (first, last, ph, cid))
    conn.commit(); conn.close()
    cust_name.set(""); cust_phone.set("")
    refresh_customers()

def delete_customer():
    sel = cust_tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Select a customer to delete")
        return
    cid = cust_tree.item(sel[0])['values'][0]
    if messagebox.askyesno("Confirm", f"Delete customer {cid}?"):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM customers WHERE customer_id = :1", (cid,))
        conn.commit(); conn.close()
        refresh_customers()

# ----- LOAN CRUD -----
def refresh_loans(search_term=""):
    loan_tree.delete(*loan_tree.get_children())
    conn = get_connection(); cur = conn.cursor()
    if search_term.strip():
        if search_term.isdigit():
            v = int(search_term)
            cur.execute("""
                SELECT loan_id, amount, interest_rate, loan_type, customer_id
                  FROM loans
                 WHERE loan_id = :1 OR customer_id = :2
            """, (v, v))
        else:
            cur.execute("""
                SELECT loan_id, amount, interest_rate, loan_type, customer_id
                  FROM loans
                 WHERE LOWER(loan_type) LIKE :1
            """, (f"%{search_term.lower()}%",))
    else:
        cur.execute("""
            SELECT loan_id, amount, interest_rate, loan_type, customer_id
              FROM loans
        """)
    for row in cur:
        loan_tree.insert("", tk.END, values=row)
    conn.close()

def add_loan():
    try:
        amt = float(loan_amount.get())
        rate = float(loan_rate.get())
        lt = loan_type.get().strip()
        cid = int(loan_cust_id.get())
    except:
        messagebox.showwarning("Input error", "Check loan fields & Customer ID")
        return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO loans(amount, interest_rate, loan_type, customer_id, start_date)
        VALUES(:1, :2, :3, :4, SYSDATE)
    """, (amt, rate, lt, cid))
    conn.commit(); conn.close()
    loan_amount.set(""); loan_rate.set(""); loan_type.set(""); loan_cust_id.set("")
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
        lt = loan_type.get().strip()
        cid = int(loan_cust_id.get())
    except:
        messagebox.showwarning("Input error", "Check loan fields & Customer ID")
        return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE loans
           SET amount        = :1,
               interest_rate = :2,
               loan_type     = :3,
               customer_id   = :4
         WHERE loan_id       = :5
    """, (amt, rate, lt, cid, lid))
    conn.commit(); conn.close()
    loan_amount.set(""); loan_rate.set(""); loan_type.set(""); loan_cust_id.set("")
    refresh_loans()

def delete_loan():
    sel = loan_tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Select a loan to delete")
        return
    lid = loan_tree.item(sel[0])['values'][0]
    if messagebox.askyesno("Confirm", f"Delete loan {lid}?"):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM loans WHERE loan_id = :1", (lid,))
        conn.commit(); conn.close()
        refresh_loans()

# ----- VIEW CUSTOMER'S LOANS -----
def view_customer_loans():
    view_tree.delete(*view_tree.get_children())
    try:
        cid = int(view_cust_id.get())
    except:
        messagebox.showwarning("Input error", "Enter a valid Customer ID")
        return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT loan_id, amount, interest_rate, loan_type, customer_id
          FROM loans
         WHERE customer_id = :1
    """, (cid,))
    for row in cur:
        view_tree.insert("", tk.END, values=row)
    conn.close()

# ----- SELECTION HANDLERS (NEW) -----
def on_customer_select(event):
    sel = cust_tree.selection()
    if not sel:
        return
    cid, fullname, phone = cust_tree.item(sel[0])['values']
    cust_name.set(fullname)
    cust_phone.set(phone)

def on_loan_select(event):
    sel = loan_tree.selection()
    if not sel:
        return
    lid, amt, rate, lt, cid = loan_tree.item(sel[0])['values']
    loan_amount.set(str(amt))
    loan_rate.set(str(rate))
    loan_type.set(lt)
    loan_cust_id.set(str(cid))

# ----- UI LAYOUT -----
app = tk.Tk()
app.title("Loan Management System")
nb = ttk.Notebook(app)
nb.pack(fill="both", expand=True, padx=5, pady=5)

# — Customers Tab —
tab1 = ttk.Frame(nb); nb.add(tab1, text="Customers")
cust_name, cust_phone, cust_search = tk.StringVar(), tk.StringVar(), tk.StringVar()

frm = ttk.Frame(tab1); frm.pack(fill="x", pady=2)
ttk.Entry(frm, textvariable=cust_search).pack(side="left", padx=5)
ttk.Button(frm, text="Search",   command=lambda: refresh_customers(cust_search.get())).pack(side="left")
ttk.Button(frm, text="Show All", command=lambda: refresh_customers("")).pack(side="left")

cols = ("CustomerID","Full Name","Phone")
cust_tree = ttk.Treeview(tab1, columns=cols, show="headings", height=6)
for c in cols: cust_tree.heading(c, text=c)
cust_tree.pack(fill="x", padx=5, pady=5)
cust_tree.bind("<<TreeviewSelect>>", on_customer_select)   

form = ttk.Frame(tab1); form.pack(fill="x", pady=5)
ttk.Label(form, text="Name:").grid(row=0,column=0)
ttk.Entry(form, textvariable=cust_name).grid(row=0,column=1)
ttk.Label(form, text="Phone:").grid(row=1,column=0)
ttk.Entry(form, textvariable=cust_phone).grid(row=1,column=1)

btns = ttk.Frame(tab1); btns.pack(pady=5)
ttk.Button(btns, text="Add",    command=add_customer).grid(row=0,column=0,padx=3)
ttk.Button(btns, text="Update", command=update_customer).grid(row=0,column=1,padx=3)
ttk.Button(btns, text="Delete", command=delete_customer).grid(row=0,column=2,padx=3)
refresh_customers()

# — Loans Tab —
tab2 = ttk.Frame(nb); nb.add(tab2, text="Loans")
loan_amount, loan_rate, loan_type, loan_cust_id, loan_search = (
    tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
)

frm2 = ttk.Frame(tab2); frm2.pack(fill="x", pady=2)
ttk.Entry(frm2, textvariable=loan_search).pack(side="left", padx=5)
ttk.Button(frm2, text="Search",   command=lambda: refresh_loans(loan_search.get())).pack(side="left")
ttk.Button(frm2, text="Show All", command=lambda: refresh_loans("")).pack(side="left")

cols2 = ("LoanID","Amount","InterestRate","LoanType","CustomerID")
loan_tree = ttk.Treeview(tab2, columns=cols2, show="headings", height=6)
for c in cols2: loan_tree.heading(c, text=c)
loan_tree.pack(fill="x", padx=5, pady=5)
loan_tree.bind("<<TreeviewSelect>>", on_loan_select)       

form2 = ttk.Frame(tab2); form2.pack(fill="x", pady=5)
ttk.Label(form2,text="Amount:").grid(row=0,column=0);   ttk.Entry(form2,textvariable=loan_amount).grid(row=0,column=1)
ttk.Label(form2,text="Rate %:").grid(row=1,column=0);  ttk.Entry(form2,textvariable=loan_rate).grid(row=1,column=1)
ttk.Label(form2,text="Type:").grid(row=2,column=0);    ttk.Entry(form2,textvariable=loan_type).grid(row=2,column=1)
ttk.Label(form2,text="Cust ID:").grid(row=3,column=0); ttk.Entry(form2,textvariable=loan_cust_id).grid(row=3,column=1)

btns2 = ttk.Frame(tab2); btns2.pack(pady=5)
ttk.Button(btns2, text="Add",    command=add_loan).grid(row=0,column=0,padx=3)
ttk.Button(btns2, text="Update", command=update_loan).grid(row=0,column=1,padx=3)
ttk.Button(btns2, text="Delete", command=delete_loan).grid(row=0,column=2,padx=3)
refresh_loans()

# — View Customer Loans Tab —
tab3 = ttk.Frame(nb); nb.add(tab3, text="View Customer Loans")
view_cust_id = tk.StringVar()

frm3 = ttk.Frame(tab3); frm3.pack(fill="x", pady=5)
ttk.Label(frm3, text="Customer ID:").pack(side="left", padx=5)
ttk.Entry(frm3, textvariable=view_cust_id, width=10).pack(side="left")
ttk.Button(frm3, text="View Loans", command=view_customer_loans).pack(side="left", padx=5)

view_tree = ttk.Treeview(tab3, columns=cols2, show="headings", height=8)
for c in cols2: view_tree.heading(c, text=c)
view_tree.pack(fill="both", expand=True, padx=5, pady=5)

app.mainloop()
