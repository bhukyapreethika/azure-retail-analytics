
import pandas as pd
import pyodbc
from itertools import combinations
from collections import Counter

# Azure SQL connection
server = 'retailserver2025-preethika.database.windows.net'
database = 'retail_db'
username = 'sqladmin'
password = 'SQL-admin' 
driver = '{ODBC Driver 17 for SQL Server}'

conn = pyodbc.connect(
    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
)

# Step 1: Load transaction data (only Basket & Product)
query = '''
    SELECT BASKET_NUM, PRODUCT_NUM
    FROM transactions
'''
df = pd.read_sql(query, conn)
conn.close()

# Step 2: Group by basket
baskets = df.groupby('BASKET_NUM')['PRODUCT_NUM'].apply(list)

# Step 3: Count product pairs
pair_counts = Counter()
for products in baskets:
    if len(products) > 1:
        pairs = combinations(sorted(set(products)), 2)
        pair_counts.update(pairs)

# Step 4: Display top product pairs
top_pairs = pair_counts.most_common(20)
print("Top 20 Most Frequently Bought Together Product Pairs:")
for pair, count in top_pairs:
    print(f"Products {pair[0]} & {pair[1]} → {count} times")

# Optional: Save to CSV
pd.DataFrame(top_pairs, columns=['Product_Pair', 'Frequency']).to_csv("basket_pairs.csv", index=False)
