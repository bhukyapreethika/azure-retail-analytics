import streamlit as st
import pandas as pd
#import pyodbc
import plotly.express as px

# Database connection settings
server = 'retailserver2025-preethika.database.windows.net'
database = 'retail_db'
username = 'sqladmin'
password = 'SQL-admin'  # Replace this
driver = '{ODBC Driver 17 for SQL Server}'

# Connect to Azure SQL
conn = pyodbc.connect(
    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
)

st.set_page_config(page_title="Retail App", layout="wide")

# Sidebar menu
page = st.sidebar.radio("📂 Select Page", ["Search by HSHD_NUM", "📊 Dashboard"])

# ------------------ PAGE 1: Search by HSHD_NUM ------------------
if page == "Search by HSHD_NUM":
    st.title("🔍 Household Transaction Explorer")
    hshd_num = st.text_input("Enter HSHD_NUM (Household ID):", value="10")

    if st.button("Search"):
        query = f"""
            SELECT
                t.HSHD_NUM,
                t.BASKET_NUM,
                t.DATE,
                t.PRODUCT_NUM,
                p.DEPARTMENT,
                p.COMMODITY,
                h.LOYALTY_FLAG,
                h.AGE_RANGE,
                h.INCOME_RANGE,
                t.SPEND,
                t.UNITS,
                t.STORE_REGION
            FROM transactions t
            JOIN products p ON t.PRODUCT_NUM = p.PRODUCT_NUM
            JOIN households h ON t.HSHD_NUM = h.HSHD_NUM
            WHERE t.HSHD_NUM = ?
            ORDER BY t.BASKET_NUM, t.DATE
        """
        df = pd.read_sql(query, conn, params=[hshd_num])

        if df.empty:
            st.warning(f"No transactions found for HSHD_NUM = {hshd_num}")
        else:
            st.success(f"Found {len(df)} transactions for HSHD_NUM = {hshd_num}")
            st.dataframe(df)

# ------------------ PAGE 2: Dashboard ------------------
elif page == "📊 Dashboard":
    st.title("📊 Retail Dashboard")
    st.markdown("Visual insights from all transactions")

    query = """
        SELECT 
            t.DATE, t.SPEND, p.DEPARTMENT, p.BRAND_TY, h.LOYALTY_FLAG
        FROM transactions t
        JOIN products p ON t.PRODUCT_NUM = p.PRODUCT_NUM
        JOIN households h ON t.HSHD_NUM = h.HSHD_NUM
    """
    df = pd.read_sql(query, conn)

    # -- Spend by Week
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    df['WEEK'] = df['DATE'].dt.isocalendar().week

    st.subheader("🗓️ Weekly Spending Trend")
    weekly = df.groupby('WEEK')['SPEND'].sum().reset_index()
    fig1 = px.line(weekly, x='WEEK', y='SPEND', title='Spend by Week')
    st.plotly_chart(fig1, use_container_width=True)

    # -- Top Departments
    st.subheader("🏬 Top 10 Departments by Total Spend")
    dept = df.groupby('DEPARTMENT')['SPEND'].sum().nlargest(10).reset_index()
    fig2 = px.bar(dept, x='DEPARTMENT', y='SPEND', title='Top Departments')
    st.plotly_chart(fig2, use_container_width=True)

    # -- Brand Type
    st.subheader("🏷️ Brand Preference: Private vs National")
    brand = df.groupby('BRAND_TY')['SPEND'].sum().reset_index()
    fig3 = px.pie(brand, names='BRAND_TY', values='SPEND', title='Brand Spend Breakdown')
    st.plotly_chart(fig3, use_container_width=True)

    # -- Loyalty Spend
    st.subheader("💳 Loyalty Flag vs Spend")
    loyalty = df.groupby('LOYALTY_FLAG')['SPEND'].sum().reset_index()
    fig4 = px.bar(loyalty, x='LOYALTY_FLAG', y='SPEND', title='Spend by Loyalty Status')
    st.plotly_chart(fig4, use_container_width=True)

conn.close()
