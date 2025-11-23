import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pyodbc

# =========================
# BASIC PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Banggood Product Analysis",
    layout="wide"
)

st.title("📊 Banggood Product Data Analysis Dashboard")

st.markdown(
    """
    This dashboard shows:
    - Cleaned product data from Banggood  
    - Exploratory analysis (Part 3)  
    - Optional SQL Server aggregated analysis (Part 5)  
    """
)

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("banggood_products_cleaned.csv")
    return df

df = load_data()

# Make sure expected columns exist
required_cols = {"category", "name", "price_raw", "rating_raw", "reviews_raw", "url"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"Missing columns in CSV: {missing}")
    st.stop()

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("Filters")

categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)

min_price = float(df["price_raw"].min())
max_price = float(df["price_raw"].max())
price_range = st.sidebar.slider(
    "Price range",
    min_value=round(min_price, 2),
    max_value=round(max_price, 2),
    value=(round(min_price, 2), round(max_price, 2))
)

min_rating = float(df["rating_raw"].min())
max_rating = float(df["rating_raw"].max())
rating_range = st.sidebar.slider(
    "Rating range",
    min_value=round(min_rating, 2),
    max_value=round(max_rating, 2),
    value=(round(min_rating, 2), round(max_rating, 2))
)

# Apply filters
filtered_df = df.copy()

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

filtered_df = filtered_df[
    (filtered_df["price_raw"] >= price_range[0]) &
    (filtered_df["price_raw"] <= price_range[1]) &
    (filtered_df["rating_raw"] >= rating_range[0]) &
    (filtered_df["rating_raw"] <= rating_range[1])
]

st.subheader("📄 Filtered Data Preview")
st.write(f"Rows after filtering: {len(filtered_df)}")
st.dataframe(filtered_df.head(20))

# =========================
# PART 3 – EXPLORATORY ANALYSIS
# =========================

st.header("🧪 Part 3 – Exploratory Data Analysis")

sns.set(style="whitegrid")

# 1. Price distribution per category (boxplot)
st.subheader("1️⃣ Price Distribution per Category")

fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.boxplot(
    data=df,
    x="category",
    y="price_raw",
    ax=ax1
)
ax1.set_title("Price Distribution per Category")
ax1.set_xlabel("Category")
ax1.set_ylabel("Price")
plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")
st.pyplot(fig1)

# 2. Rating vs Price correlation (colored by category)
st.subheader("2️⃣ Rating vs Price Correlation (Colored by Category)")

fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.scatterplot(
    data=filtered_df,
    x="price_raw",
    y="rating_raw",
    hue="category",
    ax=ax2
)
ax2.set_title("Rating vs Price Correlation")
ax2.set_xlabel("Price")
ax2.set_ylabel("Rating")
ax2.legend(title="Category", bbox_to_anchor=(1.05, 1), loc="upper left")
st.pyplot(fig2)

# 3. Top reviewed products (top 10)
st.subheader("3️⃣ Top Reviewed Products (Top 10)")

if "reviews_raw" in df.columns:
    top_reviewed = df.sort_values(by="reviews_raw", ascending=False).head(10)
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=top_reviewed,
        x="reviews_raw",
        y="name",
        ax=ax3
    )
    ax3.set_title("Top 10 Reviewed Products")
    ax3.set_xlabel("Number of Reviews")
    ax3.set_ylabel("Product Name")
    st.pyplot(fig3)

    st.write("Top reviewed products table:")
    st.dataframe(top_reviewed[["category", "name", "price_raw", "rating_raw", "reviews_raw", "url"]])
else:
    st.warning("Column 'reviews_raw' not found in data. Skipping this analysis.")

# 4. Best value metric per category (price_to_rating)
st.subheader("4️⃣ Best Value Products (Lowest Price per Rating)")

if "price_to_rating" not in df.columns:
    df["price_to_rating"] = df["price_raw"] / df["rating_raw"]

best_value = (
    df.sort_values(by="price_to_rating", ascending=True)
      .groupby("category")
      .head(5)
)

fig4, ax4 = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=best_value,
    x="price_to_rating",
    y="name",
    hue="category",
    ax=ax4
)
ax4.set_title("Best Value Products (Lowest Price per Rating) – Top 5 per Category")
ax4.set_xlabel("Price per Rating")
ax4.set_ylabel("Product Name")
st.pyplot(fig4)

st.write("Best value products table:")
st.dataframe(best_value[["category", "name", "price_raw", "rating_raw", "price_to_rating", "url"]])

# 5. Price vs Reviews (popularity proxy)
st.subheader("5️⃣ Price vs Reviews (Popularity Proxy)")

if "reviews_raw" in df.columns:
    fig5, ax5 = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        data=filtered_df,
        x="price_raw",
        y="reviews_raw",
        hue="category",
        ax=ax5
    )
    ax5.set_title("Price vs Number of Reviews")
    ax5.set_xlabel("Price")
    ax5.set_ylabel("Number of Reviews")
    ax5.legend(title="Category", bbox_to_anchor=(1.05, 1), loc="upper left")
    st.pyplot(fig5)
else:
    st.warning("Column 'reviews_raw' not found in data. Skipping this analysis.")

# =========================
# PART 5 – SQL AGGREGATED ANALYSIS
# =========================
st.header("🧮 Part 5 – SQL Aggregated Analysis")

st.markdown(
    """
    You can optionally connect to your **SQL Server** database  
    and run the aggregated queries (average price, rating, counts, etc.).
    """
)

use_sql = st.checkbox("🔌 Connect to SQL Server for aggregated metrics")

if use_sql:
    st.subheader("SQL Server Connection Settings")

    server = st.text_input("Server name", value="localhost\\SQLEXPRESS")
    database = st.text_input("Database name", value="BanggoodProducts")

    auth_type = st.radio("Authentication type", ["Windows (Trusted_Connection)", "SQL Login"])

    username = password = None
    if auth_type == "SQL Login":
        username = st.text_input("SQL Username", value="", type="default")
        password = st.text_input("SQL Password", value="", type="password")

    if st.button("Connect and Run Aggregated Queries"):
        try:
            if auth_type == "Windows (Trusted_Connection)":
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={server};DATABASE={database};Trusted_Connection=yes"
                )
            else:
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
                )

            conn = pyodbc.connect(conn_str)

            # 1. Average price per category
            avg_price = pd.read_sql_query(
                """
                SELECT category,
                       AVG(price_raw) AS average_price
                FROM Products
                GROUP BY category;
                """,
                conn
            )

            # 2. Average rating per category
            avg_rating = pd.read_sql_query(
                """
                SELECT category,
                       AVG(rating_raw) AS average_rating
                FROM Products
                GROUP BY category;
                """,
                conn
            )

            # 3. Product count per category
            product_count = pd.read_sql_query(
                """
                SELECT category,
                       COUNT(*) AS product_count
                FROM Products
                GROUP BY category;
                """,
                conn
            )

            # 4. Top 5 reviewed items (global top 5)
            top5_reviewed = pd.read_sql_query(
                """
                SELECT TOP 5 category, name, reviews_raw
                FROM Products
                WHERE reviews_raw IS NOT NULL
                ORDER BY reviews_raw DESC;
                """,
                conn
            )

            # 5. Stock availability percentage (reviews > 0 as proxy)
            stock_availability = pd.read_sql_query(
                """
                SELECT category,
                       CAST(
                           100.0 * COUNT(CASE WHEN reviews_raw > 0 THEN 1 END)
                           / COUNT(*) AS DECIMAL(10,2)
                       ) AS stock_availability_percentage
                FROM Products
                GROUP BY category;
                """,
                conn
            )

            conn.close()

            st.subheader("1️⃣ Average Price per Category (SQL)")
            st.dataframe(avg_price)

            st.subheader("2️⃣ Average Rating per Category (SQL)")
            st.dataframe(avg_rating)

            st.subheader("3️⃣ Product Count per Category (SQL)")
            st.dataframe(product_count)

            st.subheader("4️⃣ Top 5 Reviewed Products (SQL)")
            st.dataframe(top5_reviewed)

            st.subheader("5️⃣ Stock Availability Percentage (SQL)")
            st.dataframe(stock_availability)

        except Exception as e:
            st.error(f"Error connecting to SQL Server or running queries: {e}")
