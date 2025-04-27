
import pandas as pd
import pyodbc
from datetime import datetime

# Azure SQL connection
server = 'retailserver2025-preethika.database.windows.net'
database = 'retail_db'
username = 'sqladmin'
password = 'SQL-admin'  # Replace this
driver = '{ODBC Driver 17 for SQL Server}'

conn = pyodbc.connect(
    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
)

# Step 1: Query latest transaction date per household
query = '''
    SELECT HSHD_NUM, MAX(CONVERT(date, DATE)) AS last_purchase_date
    FROM transactions
    GROUP BY HSHD_NUM
'''
df = pd.read_sql(query, conn)
conn.close()

# Step 2: Convert to datetime
df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'], errors='coerce')

# Step 3: Calculate days since last purchase
today = pd.Timestamp.today()
df['days_since_last_purchase'] = (today - df['last_purchase_date']).dt.days

# Step 4: Flag churned customers (e.g. no purchase in 90+ days)
df['churn_flag'] = df['days_since_last_purchase'] > 90

# Step 5: Show result
print(df.head(10))
print("\nChurn Summary:")
print(df['churn_flag'].value_counts())

# Optional: Save to CSV
df.to_csv("churned_customers.csv", index=False)
