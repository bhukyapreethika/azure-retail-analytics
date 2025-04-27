
import pandas as pd
import pyodbc

# Replace these with your actual credentials
server = 'retailserver2025-preethika.database.windows.net'
database = 'retail_db'
username = 'sqladmin'
password = 'SQL-admin'  # Replace this!

# Set up the connection string
driver = '{ODBC Driver 17 for SQL Server}'
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Connect to Azure SQL
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# ------------------ Upload HOUSEHOLDS ------------------
households = pd.read_csv("400_households.csv")
households.columns = [
    "HSHD_NUM", "LOYALTY_FLAG", "AGE_RANGE", "MARITAL_STATUS", "INCOME_RANGE",
    "HOMEOWNER_DESC", "HH_COMP_DESC", "HOUSEHOLD_SIZE", "KID_CATEGORY_DESC"
]
households = households.replace("null", None)
households['HOUSEHOLD_SIZE'] = pd.to_numeric(households['HOUSEHOLD_SIZE'], errors='coerce')
households['KID_CATEGORY_DESC'] = households['KID_CATEGORY_DESC'].astype(str).replace('nan', None)

for _, row in households.iterrows():
    values = [None if pd.isna(v) or v == "null" else v for v in row.tolist()]
    cursor.execute("""
        INSERT INTO households (
            HSHD_NUM, LOYALTY_FLAG, AGE_RANGE, MARITAL_STATUS, INCOME_RANGE,
            HOMEOWNER_DESC, HH_COMP_DESC, HOUSEHOLD_SIZE, KID_CATEGORY_DESC
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, values)

# ------------------ Upload PRODUCTS ------------------
products = pd.read_csv("400_products.csv")
products.columns = ["PRODUCT_NUM", "DEPARTMENT", "COMMODITY", "BRAND_TY", "NATURAL_ORGANIC_FLAG"]

for _, row in products.iterrows():
    values = [None if pd.isna(v) or v == "null" else v for v in row.tolist()]
    cursor.execute("""
        INSERT INTO products (
            PRODUCT_NUM, DEPARTMENT, COMMODITY, BRAND_TY, NATURAL_ORGANIC_FLAG
        ) VALUES (?, ?, ?, ?, ?)
    """, values)

# ------------------ Upload TRANSACTIONS ------------------
transactions = pd.read_csv("400_transactions.csv")
transactions.columns = [
    "BASKET_NUM", "HSHD_NUM", "DATE", "PRODUCT_NUM", "SPEND",
    "UNITS", "STORE_REGION", "WEEK_NUM", "YEAR"
]

for _, row in transactions.iterrows():
    values = [None if pd.isna(v) or v == "null" else v for v in row.tolist()]
    cursor.execute("""
        INSERT INTO transactions (
            BASKET_NUM, HSHD_NUM, DATE, PRODUCT_NUM, SPEND,
            UNITS, STORE_REGION, WEEK_NUM, YEAR
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, values)

# Commit and close connection
conn.commit()
cursor.close()
conn.close()

print("✅ Data uploaded to Azure SQL successfully!")
