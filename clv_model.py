
import pandas as pd
import pyodbc
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score

# Connect to Azure SQL
server = 'retailserver2025-preethika.database.windows.net'
database = 'retail_db'
username = 'sqladmin'
password = 'SQL-admin' 
driver = '{ODBC Driver 17 for SQL Server}'

conn = pyodbc.connect(
    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
)

# Step 1: Get summarized household-level data
query = '''
    SELECT 
        h.HSHD_NUM,
        h.LOYALTY_FLAG,
        h.AGE_RANGE,
        h.INCOME_RANGE,
        SUM(t.SPEND) AS TOTAL_SPEND
    FROM households h
    JOIN transactions t ON h.HSHD_NUM = t.HSHD_NUM
    GROUP BY h.HSHD_NUM, h.LOYALTY_FLAG, h.AGE_RANGE, h.INCOME_RANGE
'''
df = pd.read_sql(query, conn)
conn.close()

# Step 2: Encode categorical columns
for col in ['LOYALTY_FLAG', 'AGE_RANGE', 'INCOME_RANGE']:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))

# Step 3: Train ML model
X = df.drop('TOTAL_SPEND', axis=1)
y = df['TOTAL_SPEND']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = GradientBoostingRegressor()
model.fit(X_train, y_train)

# Step 4: Evaluation
y_pred = model.predict(X_test)
print("MSE:", mean_squared_error(y_test, y_pred))
print("R²:", r2_score(y_test, y_pred))

# Step 5: Feature importance
importance = pd.Series(model.feature_importances_, index=X.columns)
print("\nFeature Importance:")
print(importance.sort_values(ascending=False))
