import oracledb

def test_connection():
    try:
        conn = oracledb.connect(
            user="loan_app",           # your app schema
            password="LoanPwd1",       # the password you set
            dsn="localhost:1521/XEPDB1"
        )
        print("✅ Connected!")
        cur = conn.cursor()
        cur.execute("SELECT USER, sys_context('USERENV','SERVICE_NAME') FROM dual")
        user, svc = cur.fetchone()
        print(f"  Logged in as: {user}")
        print(f"  Service name: {svc}")
    except oracledb.DatabaseError as e:
        err, = e.args
        print("❌ Connection failed!")
        print(f"  ORA-{err.code}: {err.message}")
    finally:
        try: conn.close()
        except: pass

if __name__ == "__main__":
    test_connection()
