
import pandas as pd
import pyodbc

# Replace these with your actual credentials
server = 'retailserver2025-preethika.database.windows.net'
database = 'retail_db'
username = 'sqladmin'
password = 'SQL-admin' 

# Connection setup
driver = '{ODBC Driver 17 for SQL Server}'
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# ---------- HOUSEHOLDS ----------
households = pd.read_csv("400_households.csv")
households.columns = [
    "HSHD_NUM", "LOYALTY_FLAG", "AGE_RANGE", "MARITAL_STATUS", "INCOME_RANGE",
    "HOMEOWNER_DESC", "HH_COMP_DESC", "HOUSEHOLD_SIZE", "KID_CATEGORY_DESC"
]
households = households.replace("null", None)
households['HOUSEHOLD_SIZE'] = pd.to_numeric(households['HOUSEHOLD_SIZE'], errors='coerce')
households['KID_CATEGORY_DESC'] = households['KID_CATEGORY_DESC'].astype(str).replace('nan', None)
household_values = [tuple(None if pd.isna(v) else v for v in row) for row in households.to_numpy()]
cursor.executemany("""
    INSERT INTO households (
        HSHD_NUM, LOYALTY_FLAG, AGE_RANGE, MARITAL_STATUS, INCOME_RANGE,
        HOMEOWNER_DESC, HH_COMP_DESC, HOUSEHOLD_SIZE, KID_CATEGORY_DESC
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", household_values)

# ---------- PRODUCTS ----------
products = pd.read_csv("400_products.csv")
products.columns = ["PRODUCT_NUM", "DEPARTMENT", "COMMODITY", "BRAND_TY", "NATURAL_ORGANIC_FLAG"]
product_values = [tuple(None if pd.isna(v) else v for v in row) for row in products.to_numpy()]
cursor.executemany("""
    INSERT INTO products (
        PRODUCT_NUM, DEPARTMENT, COMMODITY, BRAND_TY, NATURAL_ORGANIC_FLAG
    ) VALUES (?, ?, ?, ?, ?)
""", product_values)

# ---------- TRANSACTIONS ----------
transactions = pd.read_csv("400_transactions.csv")
transactions.columns = [
    "BASKET_NUM", "HSHD_NUM", "DATE", "PRODUCT_NUM", "SPEND",
    "UNITS", "STORE_REGION", "WEEK_NUM", "YEAR"
]
transaction_values = [tuple(None if pd.isna(v) else v for v in row) for row in transactions.to_numpy()]
cursor.executemany("""
    INSERT INTO transactions (
        BASKET_NUM, HSHD_NUM, DATE, PRODUCT_NUM, SPEND,
        UNITS, STORE_REGION, WEEK_NUM, YEAR
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", transaction_values)

# Finalize
conn.commit()
cursor.close()
conn.close()

print("✅ Optimized upload completed successfully!")
