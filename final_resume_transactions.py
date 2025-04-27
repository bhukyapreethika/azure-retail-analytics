
import pandas as pd
import pyodbc

# Replace with your actual credentials
server = 'retailserver2025-preethika.database.windows.net'
database = 'retail_db'
username = 'sqladmin'
password = 'SQL-admin'  

driver = '{ODBC Driver 17 for SQL Server}'
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

def batch_insert(df, sql, batch_size=1000):
    data = [tuple(None if pd.isna(v) else v for v in row) for row in df.to_numpy()]
    for i in range(0, len(data), batch_size):
        chunk = data[i:i+batch_size]
        cursor.executemany(sql, chunk)
        conn.commit()
        print(f"Inserted rows {i} to {i + len(chunk) - 1}")

# ------------------ RESUME TRANSACTIONS ------------------
print("Resuming only transactions upload (skipping existing BASKET_NUMs)...")

# Get all BASKET_NUMs already in the DB
existing_baskets = set()
cursor.execute("SELECT DISTINCT BASKET_NUM FROM transactions")
for row in cursor.fetchall():
    existing_baskets.add(row[0])

# Load and filter CSV
transactions = pd.read_csv("400_transactions.csv")
transactions.columns = [
    "BASKET_NUM", "HSHD_NUM", "DATE", "PRODUCT_NUM", "SPEND",
    "UNITS", "STORE_REGION", "WEEK_NUM", "YEAR"
]
transactions = transactions[~transactions["BASKET_NUM"].isin(existing_baskets)]

# Insert SQL
sql_transactions = '''
    INSERT INTO transactions (
        BASKET_NUM, HSHD_NUM, DATE, PRODUCT_NUM, SPEND,
        UNITS, STORE_REGION, WEEK_NUM, YEAR
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
'''
batch_insert(transactions, sql_transactions)

cursor.close()
conn.close()
print("✅ Final transaction upload completed.")
