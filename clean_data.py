import pandas as pd

# Load the scraped data into a pandas DataFrame
df = pd.read_csv("banggood_products_raw.csv")

# Print out the columns to check if 'price_raw' exists
print("Columns in the DataFrame:", df.columns)

# 1. Clean the 'price_raw' column: Remove currency symbols and convert to float
if 'price_raw' in df.columns:
    df['price_raw'] = df['price_raw'].replace({r'[^0-9.]': ''}, regex=True)  # Remove non-numeric characters
    df['price_raw'] = pd.to_numeric(df['price_raw'], errors='coerce')  # Convert to float, set errors to NaN if any
else:
    print("'price_raw' column is missing!")

# 2. Clean the 'rating_raw' column: Convert to float, handle missing values
if 'rating_raw' in df.columns:
    df['rating_raw'] = pd.to_numeric(df['rating_raw'], errors='coerce')  # Convert ratings to float, set errors to NaN
else:
    print("'rating_raw' column is missing!")

# 3. Handle missing values in 'price_raw', 'rating_raw', and 'reviews_raw'
df['price_raw'].fillna(df['price_raw'].mean(), inplace=True)  # Replace NaN prices with the mean price
df['rating_raw'].fillna(df['rating_raw'].mean(), inplace=True)  # Replace NaN ratings with the mean rating
# Fill missing reviews with 0 if 'reviews_raw' exists
if 'reviews_raw' in df.columns:
    df['reviews_raw'].fillna(0, inplace=True)  # Replace NaN reviews with 0
else:
    print("'reviews_raw' column is missing! Filling missing reviews with 0.")
    df['reviews_raw'] = 0  # If no reviews column exists, set it to 0

# 4. Create Derived Features
# 4.1 Create Price-to-Rating Ratio (how much does each unit of rating cost?)
df['price_to_rating'] = df['price_raw'] / df['rating_raw']
df['price_to_rating'].fillna(0, inplace=True)  # Handle NaN values by replacing with 0

# 4.2 Create Price-to-Review Ratio (how much does each review cost?)
df['price_to_review'] = df['price_raw'] / df['reviews_raw']
df['price_to_review'].fillna(0, inplace=True)  # Handle NaN values by replacing with 0

# Display the cleaned DataFrame (optional)
print("Cleaned DataFrame:")
print(df.head())

# Save the cleaned data with derived features to a new CSV file
output_cleaned_file = "banggood_products_cleaned.csv"
df.to_csv(output_cleaned_file, index=False, encoding="utf-8")

# Notify that the data has been saved
print(f"Cleaned data saved to {output_cleaned_file}")
