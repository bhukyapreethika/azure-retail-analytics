import pandas as pd
import pyodbc

# Replace with your actual credentials
server = 'retailserver2025-preethika.database.windows.net'
database = 'retail_db'
username = 'sqladmin'
password = 'SQL-admin'  # 🔒 Replace this!

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

# --------------------- RESUME PRODUCTS ---------------------
print("Resuming upload of products (skipping duplicates)...")

# Load existing PRODUCT_NUMs
existing_ids = set()
cursor.execute("SELECT PRODUCT_NUM FROM products")
for row in cursor.fetchall():
    existing_ids.add(row[0])

# Load and filter products
products = pd.read_csv("400_products.csv")
products.columns = ["PRODUCT_NUM", "DEPARTMENT", "COMMODITY", "BRAND_TY", "NATURAL_ORGANIC_FLAG"]
products = products[~products["PRODUCT_NUM"].isin(existing_ids)]

sql_products = """
    INSERT INTO products (
        PRODUCT_NUM, DEPARTMENT, COMMODITY, BRAND_TY, NATURAL_ORGANIC_FLAG
    ) VALUES (?, ?, ?, ?, ?)
"""
batch_insert(products, sql_products)

# --------------------- UPLOAD TRANSACTIONS ---------------------
print("Uploading transactions...")

transactions = pd.read_csv("400_transactions.csv")
transactions.columns = [
    "BASKET_NUM", "HSHD_NUM", "DATE", "PRODUCT_NUM", "SPEND",
    "UNITS", "STORE_REGION", "WEEK_NUM", "YEAR"
]

sql_transactions = """
    INSERT INTO transactions (
        BASKET_NUM, HSHD_NUM, DATE, PRODUCT_NUM, SPEND,
        UNITS, STORE_REGION, WEEK_NUM, YEAR
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
batch_insert(transactions, sql_transactions)

# --------------------- DONE ---------------------
cursor.close()
conn.close()
print("✅ Remaining upload completed successfully.")
