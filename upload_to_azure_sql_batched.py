
import pandas as pd
import pyodbc
import time

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

# Upload HOUSEHOLDS
print("Uploading households...")
households = pd.read_csv("400_households.csv")
households.columns = [
    "HSHD_NUM", "LOYALTY_FLAG", "AGE_RANGE", "MARITAL_STATUS", "INCOME_RANGE",
    "HOMEOWNER_DESC", "HH_COMP_DESC", "HOUSEHOLD_SIZE", "KID_CATEGORY_DESC"
]
households = households.replace("null", None)
households['HOUSEHOLD_SIZE'] = pd.to_numeric(households['HOUSEHOLD_SIZE'], errors='coerce')
households['KID_CATEGORY_DESC'] = households['KID_CATEGORY_DESC'].astype(str).replace('nan', None)

sql_households = """
    INSERT INTO households (
        HSHD_NUM, LOYALTY_FLAG, AGE_RANGE, MARITAL_STATUS, INCOME_RANGE,
        HOMEOWNER_DESC, HH_COMP_DESC, HOUSEHOLD_SIZE, KID_CATEGORY_DESC
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
batch_insert(households, sql_households)

# Upload PRODUCTS
print("Uploading products...")
products = pd.read_csv("400_products.csv")
products.columns = ["PRODUCT_NUM", "DEPARTMENT", "COMMODITY", "BRAND_TY", "NATURAL_ORGANIC_FLAG"]
sql_products = """
    INSERT INTO products (
        PRODUCT_NUM, DEPARTMENT, COMMODITY, BRAND_TY, NATURAL_ORGANIC_FLAG
    ) VALUES (?, ?, ?, ?, ?)
"""
batch_insert(products, sql_products)

# Upload TRANSACTIONS
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

# Finalize
cursor.close()
conn.close()
print("✅ Batched upload completed successfully.")
