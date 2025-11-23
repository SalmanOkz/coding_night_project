import pyodbc
import pandas as pd

# Load the cleaned data into a DataFrame
df = pd.read_csv("banggood_products_cleaned.csv")

# SQL Server connection details
server = 'DESKTOP-09847JI'  # e.g., 'localhost\SQLEXPRESS'
database = 'BanggoodProducts'  # Your database name

# Establish the connection to SQL Server using Windows Authentication
conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes')
cursor = conn.cursor()

# Establish the connection to SQL Server using Windows Authentication
conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes')
cursor = conn.cursor()

# 1. Average price per category
cursor.execute("""
    SELECT category, 
           AVG(price_raw) AS average_price
    FROM Products
    GROUP BY category;
""")
average_price_per_category = cursor.fetchall()
print("Average Price per Category:")
for row in average_price_per_category:
    print(f"Category: {row.category}, Average Price: {row.average_price}")

# 2. Average rating per category
cursor.execute("""
    SELECT category, 
           AVG(rating_raw) AS average_rating
    FROM Products
    GROUP BY category;
""")
average_rating_per_category = cursor.fetchall()
print("\nAverage Rating per Category:")
for row in average_rating_per_category:
    print(f"Category: {row.category}, Average Rating: {row.average_rating}")

# 3. Product count per category
cursor.execute("""
    SELECT category, 
           COUNT(*) AS product_count
    FROM Products
    GROUP BY category;
""")
product_count_per_category = cursor.fetchall()
print("\nProduct Count per Category:")
for row in product_count_per_category:
    print(f"Category: {row.category}, Product Count: {row.product_count}")

# 4. Top 5 reviewed items per category
cursor.execute("""
    SELECT category, 
           name, 
           reviews_raw
    FROM Products
    WHERE reviews_raw > 0
    ORDER BY reviews_raw DESC;
""")
top_reviewed_products = cursor.fetchall()
print("\nTop 5 Reviewed Products per Category:")
for row in top_reviewed_products:
    print(f"Category: {row.category}, Product: {row.name}, Reviews: {row.reviews_raw}")

# 5. Stock availability percentage (Using reviews as proxy)
cursor.execute("""
    SELECT category, 
           (COUNT(CASE WHEN reviews_raw > 0 THEN 1 END) / COUNT(*)) * 100 AS stock_availability_percentage
    FROM Products
    GROUP BY category;
""")
stock_availability = cursor.fetchall()
print("\nStock Availability Percentage:")
for row in stock_availability:
    print(f"Category: {row.category}, Stock Availability Percentage: {row.stock_availability_percentage}%")

# Close the connection
cursor.close()
conn.close()