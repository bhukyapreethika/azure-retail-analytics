import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Retail App", layout="wide")

# Load data
@st.cache_data
def load_data():
    transactions = pd.read_csv("400_transactions.csv")
    products = pd.read_csv("400_products.csv")
    households = pd.read_csv("400_households.csv")

    # 🧽 Clean up column names
    transactions.columns = transactions.columns.str.strip()
    products.columns = products.columns.str.strip()
    households.columns = households.columns.str.strip()

    # 🔁 Rename columns for consistency
    transactions.rename(columns={"PURCHASE_": "DATE"}, inplace=True)
    households.rename(columns={"L": "LOYALTY_FLAG"}, inplace=True)

    return transactions, products, households

# Load and merge
transactions, products, households = load_data()
merged_df = transactions.merge(products, on="PRODUCT_NUM", how="left")
merged_df = merged_df.merge(households, on="HSHD_NUM", how="left")

# Sidebar menu
page = st.sidebar.radio("📂 Select Page", ["Search by HSHD_NUM", "📊 Dashboard"])

# ------------------ PAGE 1: Search by HSHD_NUM ------------------
if page == "Search by HSHD_NUM":
    st.title("🔍 Household Transaction Explorer")
    hshd_num = st.text_input("Enter HSHD_NUM (Household ID):", value="10")

    if st.button("Search"):
        try:
            hshd_num_int = int(hshd_num)
            result = merged_df[merged_df["HSHD_NUM"] == hshd_num_int]

            if result.empty:
                st.warning(f"No transactions found for HSHD_NUM = {hshd_num}")
            else:
                st.success(f"Found {len(result)} transactions for HSHD_NUM = {hshd_num}")
                st.dataframe(result)
        except ValueError:
            st.error("Please enter a valid numeric HSHD_NUM.")

# ------------------ PAGE 2: Dashboard ------------------
elif page == "📊 Dashboard":
    st.title("📊 Retail Dashboard")
    st.markdown("Visual insights from all transactions")

    # Convert and extract week number
    merged_df["DATE"] = pd.to_datetime(merged_df["DATE"], errors='coerce')
    merged_df["WEEK"] = merged_df["DATE"].dt.isocalendar().week

    # 🗓️ Weekly Spending Trend
    st.subheader("🗓️ Weekly Spending Trend")
    weekly = merged_df.groupby("WEEK")["SPEND"].sum().reset_index()
    fig1 = px.line(weekly, x="WEEK", y="SPEND", title="Spend by Week")
    st.plotly_chart(fig1, use_container_width=True)

    # 🏬 Top Departments
    st.subheader("🏬 Top 10 Departments by Total Spend")
    dept = merged_df.groupby("DEPARTMENT")["SPEND"].sum().nlargest(10).reset_index()
    fig2 = px.bar(dept, x="DEPARTMENT", y="SPEND", title="Top Departments")
    st.plotly_chart(fig2, use_container_width=True)

    # 🏷️ Brand Preference
    st.subheader("🏷️ Brand Preference: Private vs National")
    brand = merged_df.groupby("BRAND_TY")["SPEND"].sum().reset_index()
    fig3 = px.pie(brand, names="BRAND_TY", values="SPEND", title="Brand Spend Breakdown")
    st.plotly_chart(fig3, use_container_width=True)

    # 💳 Loyalty Flag Spend
    st.subheader("💳 Loyalty Flag vs Spend")
    loyalty = merged_df.groupby("LOYALTY_FLAG")["SPEND"].sum().reset_index()
    fig4 = px.bar(loyalty, x="LOYALTY_FLAG", y="SPEND", title="Spend by Loyalty Status")
    st.plotly_chart(fig4, use_container_width=True)
