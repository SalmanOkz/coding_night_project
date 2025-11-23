# # config.py

# # Base URL for Banggood
# BASE_URL = "https://www.banggood.com"

# # Dictionary of categories and their starting subcategory URLs
# # NOTE: Replace these with actual Banggood subcategory URLs
# CATEGORIES = {
#     "Electronics": [
#         "https://www.banggood.com/Wholesale-3D-Printer-and-Supplies-ca-2002.html",
#         "https://www.banggood.com/Wholesale-3D-Printer-and-Supplies-ca-2002.html",
#         "https://www.banggood.com/Wholesale-Module-Board-ca-2278.html",
#         "https://www.banggood.com/Wholesale-Laser-Engraver-and-Supplies-ca-18981.html",
#         "https://www.banggood.com/Wholesale-Smart-Home-ca-2218.html"
#     ],
#     "Sports & Outdoor": [
#         "https://www.banggood.com/Wholesale-Camping-ca-6030.html",
#         "https://www.banggood.com/Wholesale-Fitness-Wellness-ca-6016.html",
#         "https://www.banggood.com/Wholesale-Cycling-ca-6002.html",
#         "https://www.banggood.com/Wholesale-Flashlight-ca-14002.html"
#     ],
#     # ... add other categories/urls (5 categories, 5-10 subcategories total)
# }

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the cleaned data into a DataFrame
df = pd.read_csv("banggood_products_cleaned.csv")

# Set the style for seaborn plots
sns.set(style="whitegrid")

# 1. Price Distribution per Category
plt.figure(figsize=(10, 6))
sns.boxplot(x='category', y='price_raw', data=df)
plt.title('Price Distribution per Category')
plt.xticks(rotation=90)  # Rotate x-axis labels for better readability
plt.show()  # Show the plot

# 2. Rating vs Price Correlation with Color Differentiation by Category
plt.figure(figsize=(10, 6))
sns.scatterplot(x='price_raw', y='rating_raw', data=df, hue='category', palette='tab20', s=100, edgecolor='black')

# Add title and labels
plt.title('Rating vs Price Correlation')
plt.xlabel('Price')
plt.ylabel('Rating')

# Show the plot with legend for different categories
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()  # Show the plot

# 3. Top Reviewed Products (Corrected)
top_reviewed_products = df[['name', 'reviews_raw']].sort_values(by='reviews_raw', ascending=False).head(10)

# Create a horizontal bar plot to make it easier to read long product names
plt.figure(figsize=(10, 6))
sns.barplot(x='reviews_raw', y='name', data=top_reviewed_products, palette='viridis')

# Add a title and labels
plt.title('Top Reviewed Products')
plt.xlabel('Number of Reviews')
plt.ylabel('Product Name')

# Rotate x-axis labels for better readability (if necessary)
plt.xticks(rotation=45)

# Show the plot
plt.show()


# 4. Best Value Metric per Category (Price-to-Rating ratio)
df['best_value_metric'] = df['price_raw'] / df['rating_raw']  # Best value metric: price per rating unit
best_value = df[['category', 'name', 'best_value_metric']].sort_values(by='best_value_metric').groupby('category').head(5)
plt.figure(figsize=(10, 6))
sns.barplot(x='best_value_metric', y='name', hue='category', data=best_value)
plt.title('Best Value Metric per Category')
plt.xlabel('Best Value Metric (Price per Rating)')
plt.ylabel('Product Name')
plt.show()  # Show the plot

# 5. Stock Availability Analysis (This can be assumed based on reviews and price if no stock data)
# Here we focus on identifying products with high reviews and relatively low price.
# Let's assume "stock availability" relates to popularity (high reviews) and good value (low price).
plt.figure(figsize=(10, 6))
sns.scatterplot(x='price_raw', y='reviews_raw', data=df)
plt.title('Stock Availability Analysis (Price vs Reviews)')
plt.xlabel('Price')
plt.ylabel('Number of Reviews')
plt.show()  # Show the plot
